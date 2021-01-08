from flask import Flask
from flask import render_template, redirect, url_for
from forms import SelectComDateForm, LogInForm, SelectComTimeForm, SelectZoneDateForm, SelectWardTimeForm, \
    SelectWardDateForm
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt

from db import get_db

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64


app = Flask(__name__)
bootstrap = Bootstrap(app)
bcrypt = Bcrypt(app)
app.config["SECRET_KEY"] = '79537d00f4834892986f09a100aa1edf'


@app.route("/", methods=['GET', 'POST'])
def login():
    form = LogInForm()
    if form.is_submitted():
        password = form.password.data
        # connect database and check password
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM password')
        for p in cur:
            psw = p[0]
        if bcrypt.check_password_hash(bcrypt.generate_password_hash(psw), password):
            return redirect(url_for('equity1'))
    return render_template("login.html", form=form)


@app.route("/equity1", methods=['GET', 'POST'])
#@app.route("/", methods=['GET', 'POST'])
def equity1():
    # get selected data from webpage
    form = SelectComDateForm()
    if form.is_submitted():
        company = form.company.data
        start = form.startDate.data
        end = form.endDate.data
        # data type transformation
        start = int(start)
        end = int(end)
        tmp = [":" + str(i + 1) for i in range(len(company))]
        str_com = (",".join(tmp))

        #form = SelectComDateForm()
        # connect database and retrieve data
        all_data = company
        all_data.append(start)
        all_data.append(end)
        print(all_data)
        flg = 1

        db = get_db()
        cur = db.cursor()

        sql = ('''SELECT Company, Day, Avg(PctInEquityZone) AS HourlyAvgPctInEquityZone
                                   FROM (SELECT Company, EXTRACT(Day FROM TimeStamp) AS Day, EXTRACT(HOUR FROM TimeStamp) AS Hour, PctInEquityZone
                                         FROM (SELECT TimeStamp, Company, SUM( CASE WHEN Isequityone='TRUE' THEN 1 ELSE 0 END)/COUNT(DeviceID) AS PctInEquityZone
                                               FROM DeviceLocation
                                               GROUP BY Company, TimeStamp)
                                        )
                                   WHERE Company IN (%s) AND Day >= :%d AND Day <= :%d
                                   GROUP BY Company,Day
                                   ORDER BY Company,Day''' % (str_com, start, end))
        cur.execute(sql, all_data)

        xL = []
        yL = []
        xS = []
        yS = []
        cnt = 0

        for r in cur:
            cnt = cnt + 1
            temp1 = [r[1]]
            temp2 = [r[2]]
            if (r[0] == 'Lyft'):
                xL = xL + temp1
                yL = yL + temp2
            if (r[0] == 'Spin'):
                xS = xS + temp1
                yS = yS + temp2
            print(r)

        x1 = []
        y1 = []
        x2 = []
        y2 = []

        for i in range(start, (end + 1)):
            try:
                index = xL.index(i)
            except ValueError:
                index = -1
            x1.append(i)
            if (index == -1):
                y1.append(0.0)
            else:
                y1.append(yL[index])

        for j in range(start, (end + 1)):
            try:
                index = xS.index(j)
            except ValueError:
                index = -1
            x2.append(j)
            if (index == -1):
                y2.append(0.0)
            else:
                y2.append(yS[index])

        print(x1)
        print(y1)
        print(x2)
        print(y2)

        # x = np.linspace(-2, 6, 50)

        img1 = io.BytesIO()
        plt.clf()
        if(len(company)==4):
            plt.plot(x1, y1, "-bo", label="Lyft")
            plt.plot(x2, y2, "-ro", label="Spin")
            plt.legend(loc="upper right")  # 放置位置
            plt.suptitle('Daily proportion of micromobility devices placed in equity zones by company', fontsize=10)
            plt.xlabel("Date")
            plt.ylabel("Proportion")
        elif(company[0]=="Lyft"):
            plt.plot(x1, y1, "-bo", label="Lyft")
            plt.legend(loc="upper right")  # 放置位置
            plt.suptitle('Daily proportion of micromobility devices placed in equity zones by company', fontsize=10)
            plt.xlabel("Date")
            plt.ylabel("Proportion")
        else:
            plt.plot(x2, y2, "-bo", label="Spin")
            plt.legend(loc="upper right")  # 放置位置
            plt.suptitle('Daily proportion of micromobility devices placed in equity zones by company', fontsize=10)
            plt.xlabel("Date")
            plt.ylabel("Proportion")

        # plt.figure()  # 定义一个图像窗口


        plt.savefig(img1, format='png')
        img1.seek(0)
        plt.close()

        plot_url1 = base64.b64encode(img1.getvalue()).decode()

        if(flg==1):
            return render_template("equity1_day.html", form=form, plot_url=plot_url1)

    return render_template("equity1_day.html", form=form)

@app.route("/equity2", methods=['GET', 'POST'])
def equity2():
    form = SelectComTimeForm()
    if form.is_submitted():
        company = form.company.data
        start = form.startTime.data
        end = form.endTime.data
        # data type transformation
        start = int(start)
        end = int(end)
        tmp = [":" + str(i + 1) for i in range(len(company))]
        str_com = (",".join(tmp))

        all_data = company
        all_data.append(start)
        all_data.append(end)
        print(all_data)
        flg = 1
        # connect database and retrieve data
        db = get_db()
        cur = db.cursor()

        sql = ('''SELECT Company, Hour, NumInEquityZone/NumDevices AS PctInEquityZone
                FROM (SELECT Company, EXTRACT(Hour FROM TimeStamp) AS Hour, SUM( CASE WHEN Isequityone='TRUE' THEN 1 ELSE 0 END) AS NumInEquityZone, 
                COUNT(DeviceID) AS NumDevices
                FROM DeviceLocation
                GROUP BY Company, EXTRACT(Hour FROM TimeStamp))
                WHERE Company IN (%s) AND Hour >= :%d AND Hour <= :%d
                ORDER BY Company,Hour''' % (str_com, start, end))
        cur.execute(sql, all_data)

        #for row in cur:
            #print(row)

        xL = []
        yL = []
        xS = []
        yS = []
        cnt = 0

        for r in cur:
            cnt = cnt + 1
            temp1 = [r[1]]
            temp2 = [r[2]]
            if (r[0] == 'Lyft'):
                xL = xL + temp1
                yL = yL + temp2
            if (r[0] == 'Spin'):
                xS = xS + temp1
                yS = yS + temp2
            print(r)

        x1 = []
        y1 = []
        x2 = []
        y2 = []

        for i in range(start, (end + 1)):
            try:
                index = xL.index(i)
            except ValueError:
                index = -1
            x1.append(i)
            if (index == -1):
                y1.append(0.0)
            else:
                y1.append(yL[index])

        for j in range(start, (end + 1)):
            try:
                index = xS.index(j)
            except ValueError:
                index = -1
            x2.append(j)
            if (index == -1):
                y2.append(0.0)
            else:
                y2.append(yS[index])

        print(x1)
        print(y1)
        print(x2)
        print(y2)

        # x = np.linspace(-2, 6, 50)

        # plt.figure()  # 定义一个图像窗口
        img2 = io.BytesIO()
        plt.clf()
        if(len(company)==4):
            plt.plot(x1, y1, "-bo", label="Lyft")
            plt.plot(x2, y2, "-ro", label="Spin")
            plt.legend(loc="upper center")  # 放置位置
            plt.suptitle('Hourly proportion of micromobility devices placed in equity zones by company', fontsize=10)
            plt.xlabel("Clock")
            plt.ylabel("Proportion")
        elif(company[0]=="Lyft"):
            plt.plot(x1, y1, "-bo", label="Lyft")
            plt.legend(loc="upper center")  # 放置位置
            plt.suptitle('Hourly proportion of micromobility devices placed in equity zones by company', fontsize=10)
            plt.xlabel("Clock")
            plt.ylabel("Proportion")
        else:
            plt.plot(x2, y2, "-bo", label="Spin")
            plt.legend(loc="upper center")  # 放置位置
            plt.suptitle('Hourly proportion of micromobility devices placed in equity zones by company', fontsize=10)
            plt.xlabel("Clock")
            plt.ylabel("Proportion")

        plt.savefig(img2, format='png')
        img2.seek(0)
        plt.close()

        plot_url2 = base64.b64encode(img2.getvalue()).decode()

        if(flg==1):
            return render_template("equity2_hour.html", form=form, plot_url=plot_url2)

    return render_template("equity2_hour.html", form=form)


@app.route("/parking1", methods=['GET', 'POST'])
def parking1():
    form = SelectZoneDateForm()
    if form.is_submitted():
        zone = form.zone.data
        start = form.startDate.data
        end = form.endDate.data
        # data type transformation
        start = int(start)
        end = int(end)
        tmp = [":" + str(i + 1) for i in range(len(zone))]
        str_com = (",".join(tmp))

        all_data = zone
        all_data.append(start)
        all_data.append(end)
        print(all_data)
        flg = 1
        # connect database and retrieve data
        db = get_db()
        cur = db.cursor()

        sql = ('''SELECT IsNoParkingZone, EXTRACT(Day FROM TimeStamp) AS Day, Company,
                    SUM( CASE WHEN IsNoParkingZone<>'NA' THEN 1 ELSE 0 END) AS NumInNoParkingZone
                    FROM DeviceLocation
                    WHERE IsNoParkingZone IN (%s) AND Day>= :%d AND Day<= :%d AND IsNoParkingZone<>'NA' 
                    GROUP BY ISNoParkingZone,EXTRACT(Day FROM TimeStamp),Company
                    ORDER BY ISNoParkingZone,EXTRACT(Day FROM TimeStamp),Company''' % (str_com, start, end))
        cur.execute(sql, all_data)

        dicL = {}
        dicS = {}
        for i in range(start, end+1):
            dicL[i] = 0
            dicS[i] = 0

        for r in cur:
            print(r)
            if(r[2]=="Lyft"):
                dicL[r[1]] = dicL[r[1]] + r[3]
            else:
                dicS[r[1]] = dicS[r[1]] + r[3]

        xL = []
        yL = []
        xS = []
        yS = []
        for i in range(start, end + 1):
            xL.append(i)
            xS.append(i)
            yL.append(dicL[i])
            yS.append(dicS[i])

        img3 = io.BytesIO()
        plt.clf()
        #x = [1, 2, 3, 4]
        #y = [2, 4, 6, 8]
        plt.plot(xL, yL, "-bo", label="Lyft")
        plt.plot(xS, yS, "-ro", label="Spin")
        plt.legend(loc="upper right")  # 放置位置
        plt.suptitle('Total number of parking violations in "No Parking" zones by companies', fontsize=10)
        plt.xlabel("Date")
        plt.ylabel("Number")

        plt.savefig(img3, format='png')
        img3.seek(0)
        plt.close()

        plot_url3 = base64.b64encode(img3.getvalue()).decode()

        if(flg==1):
            return render_template("parking1_number.html", form=form, plot_url=plot_url3)
        #Total number of parking violations in "No Parking" zones by companies

    return render_template("parking1_number.html", form=form)


@app.route("/parking2", methods=['GET', 'POST'])
def parking2():
    form = SelectZoneDateForm()
    if form.is_submitted():
        zone = form.zone.data
        start = form.startDate.data
        end = form.endDate.data
        # data type transformation
        start = int(start)
        end = int(end)
        tmp = [":" + str(i + 1) for i in range(len(zone))]
        str_com = (",".join(tmp))

        all_data = zone
        all_data.append(start)
        all_data.append(end)
        print(all_data)
        # connect database and retrieve data
        db = get_db()
        cur = db.cursor()

        sql = ('''WITH t1 AS (SELECT DISTINCT d1.TimeStamp, d2.ISNoParkingZone
                            FROM DeviceLocation d1
                            LEFT JOIN (SELECT DISTINCT ISNoParkingZone, TimeStamp
                                       FROM DeviceLocation
                                       WHERE IsNoParkingZone <> 'NA') d2 ON d1.TimeStamp=d2.TimeStamp)
                , t2 AS (SELECT * FROM (SELECT TimeStamp, EXTRACT(Day FROM TimeStamp) AS Day, ISNoParkingZone
                         FROM t1 )
                         PIVOT
                         ( COUNT(ISNoParkingZone)
                           FOR ISNoParkingZone IN ('Monument' Monument,'SportStadium' SportStadium,'Georgetown' Georgetown)
                          )
                         ORDER BY TimeStamp)
                , t3 AS (SELECT TimeStamp, Day, Monument, SportStadium, Georgetown, TimeStamp - LAG(TimeStamp) OVER (ORDER BY TimeStamp) AS TimeDiff
                         FROM t2)
                , t4 AS (SELECT Day, Monument * TimeDiff AS Monument, SportStadium * TimeDiff AS SportStadium, Georgetown * TimeDiff AS Georgetown
                         FROM t3)
                , DaySec AS (SELECT Day, abs(extract( day from DaySecDif))*24*60 + abs(extract( hour from DaySecDif))*60*60 
                                        + abs(extract( minute from DaySecDif))*60 AS SecDifByDay
                             FROM (SELECT Day, MAX(TimeStamp)-MIN(TimeStamp) AS DaySecDif
                                  FROM t3
                                  GROUP BY Day)
                             )    
                SELECT * 
                FROM (SELECT t4.Day,SUM(abs(extract( day from Monument ))*24*60 + abs(extract( hour from Monument ))*60*60 
                                  + abs(extract( minute from Monument ))*60)/AVG(SecDifByDay)  Monument,
                                  SUM(abs(extract( day from SportStadium ))*24*60 + abs(extract( hour from SportStadium ))*60*60 
                                  + abs(extract( minute from SportStadium ))*60)/AVG(SecDifByDay)  SportStadium,
                                  SUM(abs(extract( day from Georgetown ))*24*60 + abs(extract( hour from Georgetown ))*60*60 
                                  + abs(extract( minute from Georgetown ))*60)/AVG(SecDifByDay)  Georgetown
                      FROM t4,DaySec
                      WHERE t4.Day=DaySec.Day
                      GROUP BY t4.Day
                      ORDER BY t4.Day)
                UNPIVOT (
                   ProportionOfDay
                   For NoParkingZone
                   IN (MONUMENT AS 'Monument',
                       SportStadium AS 'SportStadium',
                       Georgetown AS 'Georgetown')
                )
                WHERE NoParkingZone IN (%s) AND Day>= :%d AND Day<= :%d''' % (str_com, start, end))
        cur.execute(sql, all_data)

        day_name = []
        perM = []
        perS = []
        perG = []
        for r in cur:
            print(r)
            day = r[0]
            cpn = r[1]
            per = r[2]
            try:
                index = day_name.index(day)
            except ValueError:
                index = -1
            if (index == -1):
                day_name.append(day)
            if (cpn == "Monument"):
                perM.append(per)
            if (cpn == "SportStadium"):
                perS.append(per)
            if (cpn == "Georgetown"):
                perG.append(per)

        print(day_name)
        print(perM)
        print(perS)
        print(perG)

        a_day_name = np.array(day_name)
        a_perM = np.array(perM)
        a_perS = np.array(perS)
        a_perG = np.array(perG)

        # print(len(zone))
        # print(len(all_data))
        # print(zone)
        # print(all_data)

        if (len(all_data) == 5):
            summ = a_perM + a_perS + a_perG
            percentage1 = a_perM
            percentage2 = a_perS
            percentage3 = a_perG
            img4 = io.BytesIO()
            plt.clf()
            plt.bar(a_day_name, percentage1, width=0.4, label="Monument")
            plt.bar(a_day_name, percentage2, width=0.4, bottom=percentage1, label="SportStadium")
            plt.bar(a_day_name, percentage3, width=0.4, bottom=percentage1 + percentage2, label="Georgetown")
            # plt.set_xticklabels(a_day_name, rotation=90)
            #plt.ylim(0, 1)
            plt.xticks(day_name)
            plt.legend(loc="upper right")
            plt.xlabel("Date")
        elif (len(zone) == 4):
            if (((zone[0] == "Monument") and (
                    zone[1] == "SportStadium"))):  # or ((zone[0]=="SportStadium") and (zone[1]=="Monument"))):
                summ = a_perM + a_perS
                percentage1 = a_perM
                percentage2 = a_perS
                plt.clf()
                img4 = io.BytesIO()
                plt.clf()
                plt.bar(a_day_name, percentage1, width=0.4, label="Monument")
                plt.bar(a_day_name, percentage2, width=0.4, bottom=percentage1, label="SportStadium")
                # plt.set_xticklabels(a_day_name, rotation=90)
                #plt.ylim(0, 1)
                plt.xticks(day_name)
                plt.legend(loc="upper right")
                plt.xlabel("Date")
            elif (((zone[0] == "Monument") and (
                    zone[1] == "Georgetown"))):  # or ((zone[0]=="SportStadium") and (zone[1]=="Monument"))):
                summ = a_perM + a_perG
                percentage1 = a_perM
                percentage2 = a_perG
                plt.clf()
                img4 = io.BytesIO()
                plt.clf()
                plt.bar(a_day_name, percentage1, width=0.4, label="Monument")
                plt.bar(a_day_name, percentage2, width=0.4, bottom=percentage1, label="Georgetown")
                # plt.set_xticklabels(a_day_name, rotation=90)
                #plt.ylim(0, 1)
                plt.xticks(day_name)
                plt.legend(loc="upper right")
                plt.xlabel("Date")
            else:
                summ = a_perS + a_perG
                percentage1 = a_perS
                percentage2 = a_perG
                plt.clf()
                img4 = io.BytesIO()
                plt.clf()
                plt.bar(a_day_name, percentage1, width=0.4, label="SportStadium")
                plt.bar(a_day_name, percentage2, width=0.4, bottom=percentage1, label="Georgetown")
                # plt.set_xticklabels(a_day_name, rotation=90)
                #plt.ylim(0, 1)
                plt.xticks(day_name)
                plt.legend(loc="upper right")
                plt.xlabel("Date")
        else:
            if (zone[0] == "Monument"):
                img4 = io.BytesIO()
                plt.plot(a_day_name, a_perM, "-bo", label="Monument")
                plt.legend(loc="upper right")
                plt.suptitle('Percentage of a day that parking violations occured in different "No Parking" zones',
                             fontsize=10)
                plt.xlabel("Date")
                plt.ylabel("Proportion")
            elif (zone[0] == "SportStadium"):
                img4 = io.BytesIO()
                plt.plot(a_day_name, a_perS, "-bo", label="SportStadium")
                plt.legend(loc="upper right")
                plt.suptitle('Percentage of a day that parking violations occured in different "No Parking" zones',
                             fontsize=10)
                plt.xlabel("Date")
                plt.ylabel("Proportion")
            else:
                img4 = io.BytesIO()
                plt.plot(a_day_name, a_perG, "-bo", label="SportStadium")
                plt.legend(loc="upper right")
                plt.suptitle('Percentage of a day that parking violations occured in different "No Parking" zones',
                             fontsize=10)
                plt.xlabel("Date")
                plt.ylabel("Proportion")

        plt.savefig(img4, format='png')
        img4.seek(0)
        plt.close()

        plot_url4 = base64.b64encode(img4.getvalue()).decode()

        if (True):
            return render_template("parking2_proportion.html", form=form, plot_url=plot_url4)
        # Percentage of a day that parking violations occured in different "No Parking" zones

    return render_template("parking2_proportion.html", form=form)


@app.route("/parking3", methods=['GET', 'POST'])
def parking3():
    form = SelectWardTimeForm()
    if form.is_submitted():
        ward = form.ward.data
        start = form.startTime.data
        end = form.endTime.data
        # data type transformation
        start = int(start)
        end = int(end)
        tmp = [":" + str(i + 1) for i in range(len(ward))]
        str_com = (",".join(tmp))

        all_data = ward
        all_data.append(start)
        all_data.append(end)
        print(all_data)
        all_data_re = all_data
        print(all_data_re)
        flg = 1
        # connect database and retrieve data
        db = get_db()
        cur = db.cursor()

        sql = (''' SELECT Ori_Ward, EXTRACT(HOUR FROM TimeStamp) AS Hour, COUNT(TripID) AS NumTrip
                FROM Trip
                WHERE Ori_Ward IN (%s) AND EXTRACT(HOUR FROM TimeStamp)>= :%d AND EXTRACT(HOUR FROM TimeStamp)<= :%d
                GROUP BY Ori_Ward, EXTRACT(HOUR FROM TimeStamp)
                ORDER BY Ori_Ward, EXTRACT(HOUR FROM TimeStamp)''' % (str_com, start, end))
        cur.execute(sql, all_data)

        x1 = []
        x2 = []
        x3 = []
        x4 = []
        x5 = []
        x6 = []
        x7 = []
        x8 = []

        y1 = []
        y2 = []
        y3 = []
        y4 = []
        y5 = []
        y6 = []
        y7 = []
        y8 = []

        for r in cur:
            print(r)
            tmpx = r[1]
            tmpy = r[2]
            if (r[0] == "1"):
                x1.append(tmpx)
                y1.append(tmpy)
            elif (r[0] == "2"):
                x2.append(tmpx)
                y2.append(tmpy)
            elif (r[0] == "3"):
                x3.append(tmpx)
                y3.append(tmpy)
            elif (r[0] == "4"):
                x4.append(tmpx)
                y4.append(tmpy)
            elif (r[0] == "5"):
                x5.append(tmpx)
                y5.append(tmpy)
            elif (r[0] == "6"):
                x6.append(tmpx)
                y6.append(tmpy)
            elif (r[0] == "7"):
                x7.append(tmpx)
                y7.append(tmpy)
            else:
                x8.append(tmpx)
                y8.append(tmpy)

        plt.clf()
        fig, axs = plt.subplots(1, 2, figsize=(8, 5))
        #fig = io.BytesIO()
        #axs = fig.subplots(1, 2, sharey=True)
        if (len(y1) != 0):
            axs[0].plot(x1, y1, "-ro", label="Ward1")
        if (len(y2) != 0):
            axs[0].plot(x2, y2, "-bo", label="Ward2")
        if (len(y3) != 0):
            axs[0].plot(x3, y3, "-go", label="Ward3")
        if (len(y4) != 0):
            axs[0].plot(x4, y4, "-co", label="Ward4")
        if (len(y5) != 0):
            axs[0].plot(x5, y5, "-ko", label="Ward5")
        if (len(y6) != 0):
            axs[0].plot(x6, y6, "-ko", label="Ward6")
        if (len(y7) != 0):
            axs[0].plot(x7, y7, "-mo", label="Ward7")
        if (len(y8) != 0):
            axs[0].plot(x8, y8, "-yo", label="Ward8")
        axs[0].legend(loc="upper right")
        plt.xlabel("Start clock")
        plt.ylabel("Number of trips")

        print(str_com)
        print(start)
        print(end)
        print(all_data)
        print(all_data_re)

        sql = (''' SELECT Des_Ward, EXTRACT(HOUR FROM TimeStamp) AS Hour, COUNT(TripID) AS NumTrip
                FROM Trip
                WHERE Des_Ward IN (%s) AND EXTRACT(HOUR FROM TimeStamp)>= :%d AND EXTRACT(HOUR FROM TimeStamp)<= :%d
                GROUP BY Des_Ward, EXTRACT(HOUR FROM TimeStamp)
                ORDER BY Des_Ward, EXTRACT(HOUR FROM TimeStamp)''' % (str_com, start, end))
        cur.execute(sql, all_data_re)

        x1e = []
        x2e = []
        x3e = []
        x4e = []
        x5e = []
        x6e = []
        x7e = []
        x8e = []

        y1e = []
        y2e = []
        y3e = []
        y4e = []
        y5e = []
        y6e = []
        y7e = []
        y8e = []

        for re in cur:
            print(re)
            tmpxe = re[1]
            tmpye = re[2]
            if (re[0] == "1"):
                x1e.append(tmpxe)
                y1e.append(tmpye)
            elif (re[0] == "2"):
                x2e.append(tmpxe)
                y2e.append(tmpye)
            elif (re[0] == "3"):
                x3e.append(tmpxe)
                y3e.append(tmpye)
            elif (re[0] == "4"):
                x4e.append(tmpxe)
                y4e.append(tmpye)
            elif (re[0] == "5"):
                x5e.append(tmpxe)
                y5e.append(tmpye)
            elif (re[0] == "6"):
                x6e.append(tmpxe)
                y6e.append(tmpye)
            elif (re[0] == "7"):
                x7e.append(tmpxe)
                y7e.append(tmpye)
            else:
                x8e.append(tmpxe)
                y8e.append(tmpye)

        #img6 = io.BytesIO()
        if (len(y1e) != 0):
            axs[1].plot(x1e, y1e, "-ro", label="Ward1")
        if (len(y2e) != 0):
            axs[1].plot(x2e, y2e, "-bo", label="Ward2")
        if (len(y3e) != 0):
            axs[1].plot(x3e, y3e, "-go", label="Ward3")
        if (len(y4e) != 0):
            axs[1].plot(x4e, y4e, "-co", label="Ward4")
        if (len(y5e) != 0):
            axs[1].plot(x5e, y5e, "-ko", label="Ward5")
        if (len(y6e) != 0):
            axs[1].plot(x6e, y6e, "-ko", label="Ward6")
        if (len(y7e) != 0):
            axs[1].plot(x7e, y7e, "-mo", label="Ward7")
        if (len(y8e) != 0):
            axs[1].plot(x8e, y8e, "-yo", label="Ward8")
        axs[1].legend(loc="upper right")
        plt.xlabel("End clock")
        plt.ylabel("Number of trips")
        plt.suptitle('Number of trips atart from / end at each Ward by hour', fontsize=10)
        img5 = io.BytesIO()
        fig.savefig(img5, format='jpg')
        img5.seek(0)
        plt.close()

        plot_url5 = base64.b64encode(img5.getvalue()).decode()

        if (True):
            return render_template("parking3_duration.html", form=form, plot_url=plot_url5)
        # Percentage of a day that parking violations occured in different "No Parking" zones

    return render_template("parking3_duration.html", form=form)




@app.route("/trip1", methods=['GET', 'POST'])
def trip1():
    form = SelectWardDateForm()
    if form.is_submitted():
        ward = form.ward.data
        start = form.startDate.data
        end = form.endDate.data
        # data type transformation
        start = int(start)
        end = int(end)
        tmp = [":" + str(i + 1) for i in range(len(ward))]
        str_com = (",".join(tmp))

        all_data = ward
        all_data.append(start)
        all_data.append(end)
        print(all_data)
        flg = 1
        # connect database and retrieve data
        db = get_db()
        cur = db.cursor()

        sql = (''' SELECT Ori_Ward AS Ward, t1.Day, (Ori_MembershipTrips+Des_MembershipTrips)/(Ori_NumTrips+Des_NumTrips) AS PctMembershipTrips
                FROM (SELECT Ori_Ward, EXTRACT(Day FROM TimeStamp) AS Day, SUM(CASE WHEN MEMBERSHIP='Member' THEN 1 ELSE 0 END) 
                             AS Ori_MembershipTrips, COUNT(TripID) AS Ori_NumTrips
                      FROM Trip
                      GROUP BY Ori_Ward, EXTRACT(Day FROM TimeStamp)
                      ) t1,
                     (SELECT Des_Ward, EXTRACT(Day FROM TimeStamp) AS Day, SUM(CASE WHEN MEMBERSHIP='Member' THEN 1 ELSE 0 END) 
                             AS Des_MembershipTrips, COUNT(TripID) AS Des_NumTrips
                      FROM Trip
                      GROUP BY Des_Ward, EXTRACT(Day FROM TimeStamp)
                      ) t2
                WHERE Ori_Ward IN (%s) AND t1.Day>= :%d AND t1.Day<= :%d 
                      AND t1.Ori_Ward=t2.Des_Ward AND t1.Day=t2.Day
                ORDER BY Ori_Ward, t1.Day''' % (str_com, start, end))
        cur.execute(sql, all_data)

        x1 = []
        x2 = []
        x3 = []
        x4 = []
        x5 = []
        x6 = []
        x7 = []
        x8 = []

        y1 = []
        y2 = []
        y3 = []
        y4 = []
        y5 = []
        y6 = []
        y7 = []
        y8 = []

        for r in cur:
            print(r)
            tmpx = r[1]
            tmpy = r[2]
            if (r[0] == "1"):
                x1.append(tmpx)
                y1.append(tmpy)
            elif (r[0] == "2"):
                x2.append(tmpx)
                y2.append(tmpy)
            elif (r[0] == "3"):
                x3.append(tmpx)
                y3.append(tmpy)
            elif (r[0] == "4"):
                x4.append(tmpx)
                y4.append(tmpy)
            elif (r[0] == "5"):
                x5.append(tmpx)
                y5.append(tmpy)
            elif (r[0] == "6"):
                x6.append(tmpx)
                y6.append(tmpy)
            elif (r[0] == "7"):
                x7.append(tmpx)
                y7.append(tmpy)
            else:
                x8.append(tmpx)
                y8.append(tmpy)

        print(x1)
        print(y1)

        img6 = io.BytesIO()
        plt.clf()
        if (len(y1) != 0):
            plt.plot(x1, y1, "-ro", label="Ward1")
        if (len(y2) != 0):
            plt.plot(x2, y2, "-bo", label="Ward2")
        if (len(y3) != 0):
            plt.plot(x3, y3, "-go", label="Ward3")
        if (len(y4) != 0):
            plt.plot(x4, y4, "-co", label="Ward4")
        if (len(y5) != 0):
            plt.plot(x5, y5, "-ko", label="Ward5")
        if (len(y6) != 0):
            plt.plot(x6, y6, "-wo", label="Ward6")
        if (len(y7) != 0):
            plt.plot(x7, y7, "-mo", label="Ward7")
        if (len(y8) != 0):
            plt.plot(x8, y8, "-yo", label="Ward8")

        plt.legend(loc="upper right")  # 放置位置
        plt.suptitle('Proportion of trips taken by members in each Ward', fontsize=10)
        plt.xlabel("Clock")
        plt.ylabel("Proportion")

        plt.savefig(img6, format='png')
        img6.seek(0)
        plt.close()

        plot_url6 = base64.b64encode(img6.getvalue()).decode()

        if (True):
            return render_template("trip1_member.html", form=form, plot_url=plot_url6)

    return render_template("trip1_member.html", form=form)


@app.route("/trip2", methods=['GET', 'POST'])
def trip2():
    form = SelectWardTimeForm()
    if form.is_submitted():
        ward = form.ward.data
        start = form.startTime.data
        end = form.endTime.data
        # data type transformation
        start = int(start)
        end = int(end)
        tmp = [":" + str(i + 1) for i in range(len(ward))]
        str_com = (",".join(tmp))

        all_data = ward
        all_data.append(start)
        all_data.append(end)
        print(all_data)
        flg = 1
        # connect database and retrieve data
        db = get_db()
        cur = db.cursor()

        sql = (''' SELECT *
                FROM (SELECT Ori_Ward AS Ward, Ori.Hour AS Hour,
                       (Ori_SumLength+Des_SumLength)/(Ori_TripFreq+Des_TripFreq) AS TripLength
                      FROM (SELECT Ori_Ward, EXTRACT(Hour FROM TimeStamp) AS Hour, COUNT(TripID) AS Ori_TripFreq, 
                             SUM(Distance) AS Ori_SumLength
                            FROM (SELECT t.TripID, t.TimeStamp, t.Ori_Ward, d.Distance
                                  FROM Trip t, Distance d
                                  WHERE t.OriginID=d.OriginID AND t.DestinationID=d.DestinationID)
                            GROUP BY Ori_Ward, EXTRACT(Hour FROM TimeStamp)) Ori,
                           (SELECT Des_Ward, EXTRACT(Hour FROM TimeStamp) AS Hour, COUNT(TripID) AS Des_TripFreq, 
                             SUM(Distance) AS Des_SumLength
                            FROM (SELECT t.TripID, t.TimeStamp, t.Des_Ward, d.Distance
                                  FROM Trip t, Distance d
                                  WHERE t.OriginID=d.OriginID AND t.DestinationID=d.DestinationID)
                            GROUP BY Des_Ward, EXTRACT(Hour FROM TimeStamp)) Des
                      WHERE Ori.Ori_Ward=Des.Des_Ward AND Ori.Hour=Des.Hour
                      ORDER BY Ori.Ori_Ward, Hour)
                WHERE Ward IN (%s) AND Hour>= :%d AND Hour<= :%d''' % (str_com, start, end))
        cur.execute(sql, all_data)

        x1 = []
        x2 = []
        x3 = []
        x4 = []
        x5 = []
        x6 = []
        x7 = []
        x8 = []

        y1 = []
        y2 = []
        y3 = []
        y4 = []
        y5 = []
        y6 = []
        y7 = []
        y8 = []

        for r in cur:
            print(r)
            tmpx = r[1]
            tmpy = r[2]
            if (r[0] == "1"):
                x1.append(tmpx)
                y1.append(tmpy)
            elif (r[0] == "2"):
                x2.append(tmpx)
                y2.append(tmpy)
            elif (r[0] == "3"):
                x3.append(tmpx)
                y3.append(tmpy)
            elif (r[0] == "4"):
                x4.append(tmpx)
                y4.append(tmpy)
            elif (r[0] == "5"):
                x5.append(tmpx)
                y5.append(tmpy)
            elif (r[0] == "6"):
                x6.append(tmpx)
                y6.append(tmpy)
            elif (r[0] == "7"):
                x7.append(tmpx)
                y7.append(tmpy)
            else:
                x8.append(tmpx)
                y8.append(tmpy)

        print(x1)
        print(y1)

        img7 = io.BytesIO()
        plt.clf()
        if (len(y1) != 0):
            plt.plot(x1, y1, "-ro", label="Ward1")
        if (len(y2) != 0):
            plt.plot(x2, y2, "-bo", label="Ward2")
        if (len(y3) != 0):
            plt.plot(x3, y3, "-go", label="Ward3")
        if (len(y4) != 0):
            plt.plot(x4, y4, "-co", label="Ward4")
        if (len(y5) != 0):
            plt.plot(x5, y5, "-ko", label="Ward5")
        if (len(y6) != 0):
            plt.plot(x6, y6, "-wo", label="Ward6")
        if (len(y7) != 0):
            plt.plot(x7, y7, "-mo", label="Ward7")
        if (len(y8) != 0):
            plt.plot(x8, y8, "-yo", label="Ward8")

        plt.legend(loc="upper right")  # 放置位置
        plt.suptitle('Average length of trips starting from or ending at each ward by hour', fontsize=10)
        plt.xlabel("Clock")
        plt.ylabel("Length")

        plt.savefig(img7, format='png')
        img7.seek(0)
        plt.close()

        plot_url7 = base64.b64encode(img7.getvalue()).decode()

        if (True):
            return render_template("trip2_length.html", form=form, plot_url=plot_url7)

    return render_template("trip2_length.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)