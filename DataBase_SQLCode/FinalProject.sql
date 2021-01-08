CREATE TABLE DeviceLocation(
    DeviceID VARCHAR(80) NOT NULL,
    Company VARCHAR(30),
    Timestamp TIMESTAMP,
    IsEquityone VARCHAR(30),
    IsNoParkingZone VARCHAR(30),
    Week NUMBER,
    Month NUMBER,
    Day NUMBER,
    PRIMARY KEY (DeviceID, Timestamp));

SELECT COUNT(*)
FROM DeviceLocation;

CREATE TABLE Distance (
    OriginID VARCHAR(30) NOT NULL,
    DestinationID VARCHAR(30) NOT NULL,
    Distance NUMBER,
    PRIMARY KEY (OriginID, DestinationID) );
SELECT * FROM Distance;

CREATE TABLE Trip(
    TripID VARCHAR(30) NOT NULL,
    Timestamp TIMESTAMP,
    /*EndTimestamp TIMESTAMP,*/
    BikeNum VARCHAR(30),
    Membership VARCHAR(30),
    Duration NUMBER,
    OriginID VARCHAR(30),
    DestinationID VARCHAR(30),
    Ori_IsEquityZone VARCHAR(20),
    Ori_WARD NUMBER,
    Des_IsEquityZone VARCHAR(20),
    Des_WARD NUMBER,
    Week NUMBER,
    Month NUMBER,
    Day NUMBER,
    PRIMARY KEY (TripID),
    FOREIGN KEY (OriginID, DestinationID) REFERENCES Distance (OriginID, DestinationID));
    
SELECT DISTINCT Month FROM Trip;


/* Grant access */
GRANT 
   SELECT,
   INSERT,
   UPDATE,
   DELETE
ON
   DeviceLocation
To zwang2;

GRANT 
   SELECT,
   INSERT,
   UPDATE,
   DELETE
ON
   Trip
To zwang2;
   
GRANT 
   SELECT,
   INSERT,
   UPDATE,
   DELETE
ON
   Distance
To zwang2;


/* Trend queries */
/* Query 1: Number and Proportion of devices placed in equity zone by each company by hour in any day*/
    
/*SELECT EXTRACT(Hour FROM TimeStamp) "Hour",
  COUNT(TimeStamp) "Frequency"
  FROM DeviceLocation
  GROUP BY EXTRACT(Hour FROM TimeStamp)
  ORDER BY "Frequency" DESC;
*/

SELECT Company, Day, Hour, Avg(NumInEquityZone) AS HourlyAvgNumInEquityZone
FROM (SELECT Company, EXTRACT(Day FROM TimeStamp) AS Day, EXTRACT(HOUR FROM TimeStamp) AS Hour, NumInEquityZone
      FROM (SELECT TimeStamp, Company, SUM( CASE WHEN Isequityone='TRUE' THEN 1 ELSE 0 END) NumInEquityZone
            FROM DeviceLocation
            GROUP BY Company, TimeStamp)
     )
GROUP BY Company,Day,Hour
ORDER BY Company,Day,Hour;

SELECT Company, Day, Hour, Avg(PctInEquityZone) AS HourlyAvgPctInEquityZone
FROM (SELECT Company, EXTRACT(Day FROM TimeStamp) AS Day, EXTRACT(HOUR FROM TimeStamp) AS Hour, PctInEquityZone
      FROM (SELECT TimeStamp, Company, SUM( CASE WHEN Isequityone='TRUE' THEN 1 ELSE 0 END)/COUNT(DeviceID) AS PctInEquityZone
            FROM DeviceLocation
            GROUP BY Company, TimeStamp)
     )
GROUP BY Company,Day,Hour
ORDER BY Company,Day,Hour;

/*
SELECT Company, Day,Hour,
       SUM( CASE WHEN Isequityone='TRUE' THEN 1 ELSE 0 END)/COUNT(DeviceID) AS PctInEquityZone
FROM (SELECT DeviceID, Company, EXTRACT(HOUR FROM TimeStamp) AS Hour, Isequityone,Day
      FROM DeviceLocation
      )
GROUP BY Company,Day,Hour
ORDER BY Company,Day, Hour;
*/

/* Query 2-4: Show the total number of parking violations in each NoParkingZone by day and company;
            Show in no parking zone, Proportion of the day where parking violations have occured;
            Show the average duration of inproperly parked vehicles */
SELECT IsNoParkingZone, Company, Day, Hour, Avg(NumInNoParkingZone) AS NumInNoParkingZone
FROM (SELECT Company, IsNoParkingZone, EXTRACT(Day FROM TimeStamp) AS Day, EXTRACT(HOUR FROM TimeStamp) AS Hour, NumInNoParkingZone
      FROM (SELECT TimeStamp, Company, IsNoParkingZone, SUM( CASE WHEN IsNoParkingZone<>'NA' THEN 1 ELSE 0 END) AS NumInNoParkingZone
            FROM DeviceLocation
            WHERE IsNoParkingZone<>'NA'
            GROUP BY Company, TimeStamp,ISNoParkingZone)
     )
GROUP BY Company,Day,Hour,IsNoParkingZone
ORDER BY IsNoParkingZone,Company,Day,Hour;

/* Query 5: Show the number of trips originating/ending in each Ward by Day and Hour of March 2020 */
SELECT Ori_Ward, EXTRACT(Day FROM TimeStamp) AS Day, EXTRACT(HOUR FROM TimeStamp) AS Hour, Sum(NumTrip) AS HourlyNumTrip
FROM (SELECT TimeStamp,Ori_Ward,COUNT(TripID) AS NumTrip
      FROM Trip
      GROUP BY TimeStamp,Ori_Ward)
GROUP BY Ori_Ward, EXTRACT(Day FROM TimeStamp), EXTRACT(HOUR FROM TimeStamp)
ORDER BY Ori_Ward, EXTRACT(Day FROM TimeStamp), EXTRACT(HOUR FROM TimeStamp);

SELECT Des_Ward, EXTRACT(Day FROM TimeStamp) AS Day, EXTRACT(HOUR FROM TimeStamp) AS Hour, Sum(NumTrip) AS HourlyNumTrip
FROM (SELECT TimeStamp,Des_Ward,COUNT(TripID) AS NumTrip
      FROM Trip
      GROUP BY TimeStamp,Des_Ward)
GROUP BY Des_Ward, EXTRACT(Day FROM TimeStamp), EXTRACT(HOUR FROM TimeStamp)
ORDER BY Des_Ward, EXTRACT(Day FROM TimeStamp), EXTRACT(HOUR FROM TimeStamp);

/* Query 6: Show the proportion of trips (starting from or ending at) taken by members in each Ward in each day of March 2020 */
SELECT Ori_Ward AS Ward, t1.Day, (Ori_MembershipTrips+Des_MembershipTrips)/(Ori_NumTrips+Des_NumTrips) AS PctMembershipTrips
FROM (SELECT Ori_Ward, EXTRACT(Day FROM TimeStamp) AS Day, SUM(MembershipTrips) AS Ori_MembershipTrips, SUM(NumTrips) AS Ori_NumTrips
      FROM (SELECT TimeStamp,Ori_Ward,SUM(CASE WHEN MEMBERSHIP='Member' THEN 1 ELSE 0 END) AS MembershipTrips, COUNT(TripID) AS NumTrips
            FROM Trip
            GROUP BY TimeStamp,Ori_Ward)
      GROUP BY Ori_Ward, EXTRACT(Day FROM TimeStamp)
      ) t1,
     (SELECT Des_Ward, EXTRACT(Day FROM TimeStamp) AS Day, SUM(MembershipTrips) AS Des_MembershipTrips, SUM(NumTrips) AS Des_NumTrips
      FROM (SELECT TimeStamp,Des_Ward,SUM(CASE WHEN MEMBERSHIP='Member' THEN 1 ELSE 0 END) AS MembershipTrips, COUNT(TripID) AS NumTrips
            FROM Trip
            GROUP BY TimeStamp,Des_Ward)
      GROUP BY Des_Ward, EXTRACT(Day FROM TimeStamp)
      ) t2
WHERE t1.Ori_Ward=t2.Des_Ward AND t1.Day=t2.Day
ORDER BY Ori_Ward, t1.Day;


/* Query 7: Show how average trip length changes by day and hour in each ward ? */
SELECT Ori_Ward AS Ward, Ori.Day, Ori.Hour,
       (Ori_TripFreq*Ori_Length+Des_TripFreq*Des_Length)/(Ori_TripFreq+Des_TripFreq) AS TripLength
FROM (SELECT Ori_Ward, EXTRACT(Day FROM TimeStamp) AS Day, EXTRACT(Hour FROM TimeStamp) AS Hour, SUM(TripID) AS Ori_TripFreq, AVG(Distance) AS Ori_Length
      FROM (SELECT t.TripID, t.TimeStamp, t.Ori_Ward, d.Distance
            FROM Trip t, Distance d
            WHERE t.OriginID=d.OriginID AND t.DestinationID=d.DestinationID)
      GROUP BY Ori_Ward, EXTRACT(Day FROM TimeStamp), EXTRACT(Hour FROM TimeStamp)) Ori,
     (SELECT Des_Ward, EXTRACT(Day FROM TimeStamp) AS Day, EXTRACT(Hour FROM TimeStamp) AS Hour, SUM(TripID) AS Des_TripFreq, AVG(Distance) AS Des_Length
      FROM (SELECT t.TripID, t.TimeStamp, t.Des_Ward, d.Distance
            FROM Trip t, Distance d
            WHERE t.OriginID=d.OriginID AND t.DestinationID=d.DestinationID)
      GROUP BY Des_Ward, EXTRACT(Day FROM TimeStamp), EXTRACT(Hour FROM TimeStamp)) Des
WHERE Ori.Ori_Ward=Des.Des_Ward AND Ori.Day=Des.Day AND Ori.Hour=Des.Hour;

