# Municipal Micromobility Management System

## Contributors to this project
Xiang Yan, Ziying Wang, and Manzhu Wang developed the initial database management system in the COP 5725 Database Management Sytem class offered at the University of Florida. With resources available at the UF SERMOS lab, Xiang Yan, Yepeng Liu, and Xilei Zhao have been continuing developing the database by refining and adding functionalities.


## Background
Micromobility services such as e-scooter and e-bike sharing have quickly become popular across cities around the world. To make micromobility better serve the residents, many city governments have passed regulations to manage the operation of micromobility services (see an example from Washington DC here https://ddot.dc.gov/page/dockless-vehicle-permits-district). Underlying these regulations lies the needs to address the following: 
        *a. Equity. To make sure that low-income people have adequate access to micromobility options, cities often require micromobility companies to place a certain proportion (e.g., 20%) of their vehicles/devices in predefined equity zones. When this policy is in place (e.g. it is implemented in Washington DC), the government need to monitor if the micromobility companies has complied with it. This calls for a need for analysts to examine the proportion of micromobility devices placed by each company in the equity zones over time. For instance, on a monthly basis, which company has the best compliance record in from February to October 2020? How does the proportion of micromobility devices being placed in equity zones change by hour of day? What are the daily number of micromobility devices being placed in each equity zone from February to October 2020? 
        *b. Parking violations. A main concern that the public has expressed on micromobility is improper parking (e.g., an e-scooter being parked on the sidewalk), which impedes travel by other modes. In response to this problem, cities often require micromobility companies to urge their customers to only park at designated zones. If parking violations occur, the city government or the micromobility company needs to quickly relocate the vehicle to appropriate parking space. To facilitate this procedure, analysts should help city governments understand the number of micromobility devices inappropriately parked in different parts of the city over time. For instance, how does the number of inappropriately parked micromobility devices in change by each week? From February to October 2020, which parts of the city (the city is divided into six wards) are experiencing a growth in inappropriately parked micromobility devices on a monthly basis?
        *c. Trip characteristics. A primary responsibility of city governments is to manage the infrastructure for a variety of mobility options, ranging from driving, to public transit, and to micromobility. Doing so requires cities to understand the trends of trip characteristics for different travel modes. Specifically, to better manage micromobility services, cities need to understand how people have traveled with micromobility devices over time and across space. COVID-19 has made this need even more important as COVID has significantly changed people’s travel behavior. Examples of important trend analysis include: What are the weekly total number of e-scooter trips that people have made in Washington DC from February to October 2020? What are the average trip length in each month? How does the monthly number of e-scooter trips change in different parts of the city?
    The purpose of this project is to develop a municipal micromobility management system (MMMS) that would allow city governments to efficiently accommodate the above needs. Currently, many cities that allow the operation of micromobility services have already mandated micromobility operators to share two types of data: the real-time availability of micromobility devices (e.g., the geographic locations of idle micromobility devices in real time), and the micromobility trip data (usually reported on a quarterly basis). The former will be shared with the public through open APIs, and the latter will be shared with the city only. The specific goals of the MMMS are to store and catalog these data, to allow the city to monitor and evaluate the micromobility operations, to inform the public regarding the micromobility operations, and to solicit feedback from the public on how to improve micromobility services and the supporting infrastructure.

## Functionality
We envision the MMMS to have the following functionalities:
a.	Extract the real-time micromobility availability data from operator-provided APIs, catalog the data, and store them.
b.	Catalog and store the historic micromobility trip data. The data should contain micromobility trip records that show the following characteristics: locations of origins and destinations, start time, end time, distance, duration, and cost.
c.	Allow analysts to compute the percentage of micromobility devices placed in equity zones at any given moment and allow them to further aggregate the data over time (daily, weekly, or monthly) and across space (the city can be divided into six wards) to facilitate trend analysis.
d.	Allow analysts to calculate the percentage of time in a day that each micromobility operator has complied with the equity-zone required. Allow analysts to aggregate the data so that they can examine weekly or month trends.
e.	Enable the city to detect the incident if a micromobility device has been parked at prohibited space and to subsequently trigger a notification to the operator of that device. Allow the city to count the number of inappropriately parked micromobility devices at a given zone at any moment. Furthermore, allow the analysts to aggregate the data over time (daily, weekly, or monthly) and across space to do trend analysis.
f.	Allow analysts to examine the characteristics of micromobility trips and to analyze their patterns over time. For instance, analyze should be able to answer: what is the average micromobility trip length for each month in 2020?

## Database structure and data sources
The municipal micromobility management system consists of tables:
Database elements	Description
Availability	Contains the real-time micromobility availability data from operator-provided APIs. The attributes of the table include the following: timestamp, operator, device id, latitude of device, longitude of device
Trip	Contains the micromobility trips provided by each operator. The attributes of the table include the following: operator, latitude of trip origin, longitude of trip origin, latitude of trip destination, longitude of trip destination, trip start timestamp, trip end timestamp, distance, duration, and cost.
Equity zone	A geoJSON file that denotes the boundary of equity zones. This file can be joined with the “Availability” and “Trip” files to determine if an available micromobility device is within the equity zone and if a micromobility trip starts or ends within the equity zone.
Prohibited parking zone	A geoJSON file that denotes the boundary of prohibited parking zones. This file can be joined with the “Availability” file to determine if a micromobility device is parked in a prohibited space.
Parking violations	A table that records the parking violations reported by the public. The table will record the following attributes: timestamp (i.e., when the violation is observed), and latitude and longitude of the reported violations.
Crash incidents	A table that records the incidents of crashes or near-misses reported by the public. The table will record the following attributes: timestamp1 (i.e., when the incident is observed), timestamp2 (when the user entered the information), and latitude and longitude of the reported incident.
Parking space need	A table that records the locations where users have identified a need for additional parking space. The table will record the following attributes: timestamp (when the user entered the information), street name, and latitude and longitude of the marked location.
Infrastructure need	A table that records the locations where users have identified a need for additional biking infrastructure. The table will record the following attributes: timestamp (when the user entered the information), street name, and latitudes and longitudes of the marked location.

      We will develop our database management system in the context of Washington DC. The data are all publicly available through government websites:
a.	Micromobility-related (“availability” and “trip”) data are accessible from https://ddot.dc.gov/page/dockless-api
b.	“Equity zone” and “Prohibited parking zone” are predefined by the District Department of Transportation, and the geoJSON files are accessible from https://opendata.dc.gov/.
c.	The other database elements will be crowdsourced from potential users of the MMMS.

## E-R diagram
To develop a data management system that can allow analysts to conduct the trend analysis specified in Phase 1 of our project, we come up with the following conceptual database design. The E-R Diagram of the proposed municipal micromobility management system (MMMS) is shown in Figure 1. The database system will contain the following entities: Device Location, Company, Equity Zone, No Parking Zone, Trip, Distance, and Ward Boundary. The attributes of these entities and their relationships are described as follows:
•	Device Location shows the location of micromobility devices at a given moment. It contains the following attributes: device location ID, timestamp, device ID, company name, latitude, and longitude. Moreover, it contains the following derived attributes (based on the timestamp attribute): month, week, day.
•	Each device belongs to a company. A company’s attributes include company name and the fleet size (i.e., the number of micromobility devices it owns).
•	The location where a micromobility device parks is either in or not in a equity zone. The Equity Zone entity set is a set of spatial data object (polygon type) that delineates the boundary of equity zones. The boundaries of the equity zones may change over time and so we make it an entity set rather than an attribute of Device Location.
•	The location where a micromobility device parks is either in or not in a parking prohibited zone. The No Parking Zone entity set is a spatial data object that delineates the boundary of parking prohibited zones. The boundaries of the no parking zones may change over time and so we make it an entity set rather than an attribute of Device Location.
 
Figure 1. E-R Diagram of municipal micromobility management system

•	The Trip entity set includes the following attributes: Trip ID, start timestamp, end timestamp, origin ID, and destination ID. It also contains the following derived attributes (from the start timestamp): duration, month, week, and hour.
•	The network distance between each pair of origin ID and destination ID is stored in the Distance entity set. The distance entity set contains four attributes: O-D pair (composite attribute based on origin ID and destination ID), origin ID, destination ID, and distance.
•	Trips take place (start from or end at) at different Wards (DC has six wards). The Ward Boundary entity set is a spatial data object (polygon type) that delineates the boundary of each ward.

## User Interfact Design
Municipal Micromobility Management System contains three main sections, which contain six pages in total, in addition, a login page will also be included in the website. Government analysts are the main users of the site. The connecting of the pages is shown in figure2. 
Figure 2. connecting of the pages in municipal micromobility management system
Page 1: Login page
Users have to use their work account and password to login. After users entering the correct account password, the page will jump to the function selection page (Page 2).
Page 2: Function selection
Users can select the functional section that they want to use in this page, the website will jump to the first page of that section. If one needs to use other functional pages, they can jump through the button at the top of the pages.
1.1.	Functional section 1: Equity Monitor
Page 3: Number of devices in equity zones
This page allows the users to analyze the number of micromobility devices placed in equity zones by each company. Users can select the companies that they are interested in, and a histogram will show the changes of the total micromobility numbers in equity zones from January 2020 to October 2020, each company represented by a column. If more than one companies are select, the columns will be superimposed to show the contrast.
Page 4: Proportion of devices in equity zones
This page allows the analysts to analyze the proportion of micromobility devices placed by each company in equity zones over time. Users can select the date, and a line chart will show the change of the proportion of micromobility devices in equity zones over the 24-hour period. Users can also select a month (or week), which allows them to examine the monthly (weekly) trend from January 2020 to October 2020. Users will also be allowed to examine the hourly, weekly, monthly trends by company.
1.2.	Functional section 2: Parking Management
Page 5: Analysis of improper parking
This page allows the users to analyze improper parking across the six wards of Washington DC. Users can select a ward and a month, and a line chart will show the number of micromobility devices that are parked in “no parking zones” for each day of the selected month in the select ward. Multiple lines will be displayed if the user has selected more than one ward.
1.3.	Functional section 3: Trip Analysis
Page 6: Analysis of average trip length
This page allows the users to analyze the average length of micromobility trips in a selected period of time. Users can select to view weekly or monthly trends. For instance, users can select three months, and a histogram will show the change of the average trip length in each week during that three months.
Page 7: Analysis of trip numbers
This page allows the users to analyze the total number of micromobility trips. A line chart will show the change of weekly number of micromobility trips that people have made in the city from February to October 2020. The users can also select to visualize the trips happened in different wards, in which case the trip frequency will be aggregated by ward and separate lines will be shown for each ward.
Page 8: Analysis of trips by company
This page allows the users to analyze the total number of trips for each company. Users can select the companies, and each company will be represented by a line, the lines will show the changes of each company’s monthly trips from February 2020 to October 2020.


## Implementation
      The system mainly consists of three parts:
a.	Database interface
      The database tables will be built in Oracle which is a database for Internet oriented computing environment. Oracle database system is a popular relational database management system and can provide support for the construction of C/S system effectively.
b.	Admin zone
      Admin zone is also called back-end in the website, where the functions are finished. In the MMMS, the analyses will be realized through Python just after the data extracted from the database. Cx_Oracle is a Python extension module that enables access to Oracle Database, and to establish the connection between the admin zone and the database tables, such a module will be installed from PyPI.
c.	User interface
      User interface refers to the front-end of the web application and is responsible for the interaction with the users. Users can select the function to be used in this interface and get the outputs easily. This interface will be accomplished by Flask which is a lightweight Web application framework written in Python. A major advantage of choosing this framework is that Flask is very friendly for the construction of a Web application with simple requirements and short project life, which 's exactly what characterizes our program. Meanwhile, it can also be achieve more complex functionalities by adding a large number of plug-ins available.
