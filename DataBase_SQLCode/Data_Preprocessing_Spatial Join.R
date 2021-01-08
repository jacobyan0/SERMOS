setwd("D:/Dropbox (UFL)/Master's Degree/COP5725 Database management systems/COP5725 Final project/Data/GIS")

library(sf)
library(dplyr)
library(spData)
library(ggplot2)
library(sp)
library(maptools)
library(lubridate)

## Read and pre-processing the data
# EquityZone
EquityZone <- read_sf(dsn="Dockless_Equity_Emphasis_Areas.shp")
# Dissolve --> one can put SHAPEAREA=sum(SHAPEAREA) into summarise()
EquityZone <- EquityZone %>% summarise()

# DC wards
Wards <- read_sf(dsn="Ward_from_2012.shp")
## Keep ward number and geometry only
Wards<-Wards[,c("WARD","geometry")]

# No Parking Zone
NoParkingZone1 <- read_sf(dsn="Dockless_Bikes_and_Scooter_Georgetown_Geofence_Restrictions.shp")
NoParkingZone2 <- read_sf(dsn="Dockless_Bikes_and_Scooter_Monument_Map.shp")
NoParkingZone3 <- read_sf(dsn="Dockless_Bikes_and_Scooter_Sport_Stadium_Geofences.shp")
NoParkingZone1 <- NoParkingZone1%>% summarise()
NoParkingZone2 <- NoParkingZone2%>% summarise()
NoParkingZone3 <- NoParkingZone3%>% summarise()

NoParkingZone1$NoParkingZone<-'Georgetown'
NoParkingZone2$NoParkingZone<-'Monument'
NoParkingZone3$NoParkingZone<-'SportStadium'

NoParkingZone1<-st_cast(NoParkingZone1,"POLYGON")
NoParkingZone2<-st_cast(NoParkingZone2,"POLYGON")
NoParkingZone3<-st_cast(NoParkingZone3,"POLYGON")

### For some reason, NoParkingZone1's dimension is XYZ, need to convert to XY
NoParkingZone1 <- st_zm(NoParkingZone1,drop = TRUE)

## Merge no parking zone
NoParkingZone<- rbind(NoParkingZone1,NoParkingZone2,NoParkingZone3)
rm(NoParkingZone1,NoParkingZone2,NoParkingZone3)

#################################################################################
#### Processing availability data  ##############################################
#################################################################################
DeviceLocation<-read.csv(file="D:/Dropbox (UFL)/Master's Degree/COP5725 Database management systems/COP5725 Final project/Data/Availability/All.csv")
## Convert to spatial object, geographic coordination system is WGS84
DeviceLocation_sf = st_as_sf(DeviceLocation, coords = c("lon", "lat"), crs = 4326, agr = "constant")

### Spatial join -- Equity Zone
IfEquityZone<- st_intersects(DeviceLocation_sf,EquityZone,sparse = FALSE)
DeviceLocation_sf$IsEquityZone <- IfEquityZone
rm(IfEquityZone)
#prop.table(table(DeviceLocation_sf$IsEquityZone)) 0.8 FALSE; 0.2 TRUE

### Spatial join --- NoParkingZone: If NA, is not in NoParkingZone, else in one of three
DeviceLocation_sf <- st_join(DeviceLocation_sf,NoParkingZone)

### Convert from Epoch Time to EST
library(lubridate)
DeviceLocation_sf<-DeviceLocation_sf
DeviceLocation_sf$timestamp <- lubridate::as_datetime(DeviceLocation_sf$timestamp,tz="US/Eastern")

### Create Week and Month fields
DeviceLocation_sf$Date <- as.Date(DeviceLocation_sf$timestamp,tz="US/Eastern","%Y-%m-%d")
startDate <- "2020-02-29"   ### select first Monday
DeviceLocation_sf$Week <- floor(as.numeric(difftime(DeviceLocation_sf$Date,startDate,units="weeks")))+1 ## calculate week order. start with 1
DeviceLocation_sf$Month <- month(DeviceLocation_sf$Date)
DeviceLocation_sf$Day <- day(DeviceLocation_sf$Date)
DeviceLocation_sf <- DeviceLocation_sf[,!names(DeviceLocation_sf) %in% c("Date")]

### From spatial object to nonspatial object
st_geometry(DeviceLocation_sf) <- NULL

write.csv(DeviceLocation_sf,file="D:/Dropbox (UFL)/Master's Degree/COP5725 Database management systems/COP5725 Final project/Data/ToOracleSQL/DeviceLocation.csv",row.names = FALSE)

#################################################################################
#### Processing trip data  ######################################################
#################################################################################
Trips<-read.csv(file="D:/Dropbox (UFL)/Master's Degree/COP5725 Database management systems/COP5725 Final project/Data/Trip data/202003-capitalbikeshare-tripdata.csv")
XY<-read.csv(file="D:/Dropbox (UFL)/Master's Degree/COP5725 Database management systems/COP5725 Final project/Data/Trip data/BikeShare_XY.csv")
colnames(XY) <- c("StationID","StationNum","Lat","Lon")

Trips<-merge(Trips,XY,by.x="StartStationNum",by.y="StationNum")
colnames(Trips)<-c("StartStationNum","Duration","StartTimeStamp","EndTimeStamp","EndStationNum","BikeNum","Membership",
                   "StartStationID","Ori_Lat","Ori_Lon")
Trips<-merge(Trips,XY,by.x="EndStationNum",by.y="StationNum")
colnames(Trips)<-c("EndStationNum","StartStationNum","Duration","StartTimeStamp","EndTimeStamp","BikeNum","Membership",
                   "StartStationID","Ori_Lat","Ori_Lon","EndStationID","Des_Lat","Des_Lon")
Trips$ID<-1:length(Trips$StartTimeStamp)
Trips<-Trips[,c("ID","StartTimeStamp","BikeNum","Membership","Duration",
                "StartStationID","Ori_Lat","Ori_Lon","EndStationID","Des_Lat","Des_Lon")]

## Convert to spatial object, geographic coordination system is WGS84
Trips.Ori = st_as_sf(Trips, coords = c("Ori_Lon", "Ori_Lat"), crs = 4326, agr = "constant")
Trips.Des = st_as_sf(Trips, coords = c("Des_Lon", "Des_Lat"), crs = 4326, agr = "constant")

### Spatial join -- if trip starts or ends in Equity Zone
IfEquityZone<- st_intersects(Trips.Ori,EquityZone,sparse = FALSE)
Trips.Ori$Ori_IsEquityZone <- IfEquityZone
rm(IfEquityZone)
#prop.table(table(DeviceLocation_sf$IsEquityZone)) 0.8 FALSE; 0.2 TRUE

IfEquityZone<- st_intersects(Trips.Des,EquityZone,sparse = FALSE)
Trips.Des$Des_IsEquityZone <- IfEquityZone
rm(IfEquityZone)

### Spatial join --- WhichWard belows to
TripsOriWard<- st_join(Trips.Ori,Wards)
TripsOriWard <- TripsOriWard[-which(is.na(TripsOriWard$WARD)),]
colnames(TripsOriWard)<-c("ID","TimeStamp","BikeNum","Membership","Duration",
                          "StartStationID","EndStationID","Des_Lat","Des_Lon","Ori_IsEquityZone","Ori_WARD","geometry")
#TripsOriWard[,c("ID","TimeStamp","BikeNum","Membership","Duration",
#                              "StartStationID","EndStationID","Des_Lat","Des_Lon","Ori_WARD")]
TripsOriWard<-TripsOriWard[,c("ID","TimeStamp","BikeNum","Membership","Duration",
                              "StartStationID","EndStationID","Ori_IsEquityZone","Ori_WARD")]

TripsDesWard<- st_join(Trips.Des,Wards)
TripsDesWard <- TripsDesWard[-which(is.na(TripsDesWard$WARD)),]
colnames(TripsDesWard)<-c("ID","TimeStamp","BikeNum","Membership","Duration",
                          "StartStationID","EndStationID","Ori_Lat","Ori_Lon","Des_IsEquityZone","Des_WARD","geometry")
TripsDesWard<-TripsDesWard[,c("ID","Des_IsEquityZone","Des_WARD")]
#TripsDesWard<-TripsDesWard[,c("ID","Ori_Lat","Ori_Lon","Des_WARD")]

### From spatial object to nonspatial object0000
st_geometry(TripsOriWard) <- NULL
st_geometry(TripsDesWard) <- NULL
Trips<-merge(TripsOriWard,TripsDesWard,by="ID")

### Create Week and Month,Day fields based on StartTimeStamp
Trips$Date <- as.Date(Trips$TimeStamp,tz="US/Eastern","%m/%d/%y")
startDate <- "2020-02-29"   ### select first Monday
Trips$Week <- floor(as.numeric(difftime(Trips$Date,startDate,units="weeks")))+1 ## calculate week order. start with 1
Trips$Month <- month(Trips$Date)
Trips$Day <- day(Trips$Date)
Trips <- Trips[,!names(Trips) %in% c("Date")]

#st_geometry(Trips) <- NULL

write.csv(Trips,file="D:/Dropbox (UFL)/Master's Degree/COP5725 Database management systems/COP5725 Final project/Data/ToOracleSQL/Trips.csv",row.names = FALSE)
