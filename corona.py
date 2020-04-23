import math
import os
from datetime import timedelta, datetime, date

import pandas as pd
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox

from data import generateData

# create directories and csv files
countryList, countryDate = generateData()
size = (len(countryList) * 2) + 1

choose = 0
countrySelect = 0
caseSelect = 0
select = 0


def setChoose(value):
    global choose
    choose = value


def setCountrySelect(value):
    global countrySelect
    countrySelect = value


def setCaseSelect(value):
    global caseSelect
    caseSelect = value


def setSelect(value):
    global select
    select = value


def readCsv():
    countries = "Countries"

    if select % 2 != 0:
        count = int(select / 2)
        doc = countries + "/" + countryList[count] + "/case.csv"
        title = countryList[count] + " Total Cases "
    else:
        count = int(select / 2) - 1
        doc = countries + "/" + countryList[count] + "/death.csv"
        title = countryList[count] + " Total Deaths "

    df = pd.read_csv(doc, sep=",")
    x = df.dayNo.values.reshape(-1, 1)
    y = df.case.values.reshape(-1, 1)

    if select % 2 != 0:
        plt.title(countryList[count].upper() + " CASE GRAPH")
        plt.ylabel("Case")
    else:
        plt.title(countryList[count].upper() + " DEATH GRAPH")
        plt.ylabel("Death")
    plt.xlabel("Day")

    return title, x, y


def ml(x, y, degree):
    from sklearn.linear_model import LinearRegression

    lr = LinearRegression()
    lr.fit(x, y)

    from sklearn.preprocessing import PolynomialFeatures

    pr = PolynomialFeatures(degree=degree)

    x_polynomial = pr.fit_transform(x)
    lr2 = LinearRegression()
    lr2.fit(x_polynomial, y)

    y_head = lr2.predict(x_polynomial)

    return y_head, lr2, pr


def predict(lr2, pr, number):
    return lr2.predict(pr.fit_transform([[number]]))


def plot(degree):
    title, x, y = readCsv()
    plt.scatter(x, y)
    plt.show()

    color = ""
    if caseSelect == 1:
        color = "purple"
    elif caseSelect == 2:
        color = "red"

    graph = "Graph"
    if not os.path.exists(graph):
        os.mkdir(graph)

    y_head, lr2, pr = ml(x, y, degree)
    plt.plot(x, y_head, color=color, label="Degree " + str(degree))
    plt.legend()
    title, x, y = readCsv()
    plt.scatter(x, y)
    saveTitle = title.replace(" ", "_").lower() + ".png"
    plt.savefig(graph + "/" + saveTitle)
    plt.show()

    return title


def generateDate(dateList, count):
    d = date(dateList[0], dateList[1], dateList[2]) + timedelta(days=count)
    dateFormat = str(d.strftime('%B %d'))
    return dateFormat


def dateCompress(begin, finish, count):
    start = date(2020, begin[0], begin[1]) + timedelta(days=count)
    delta = finish - start
    return delta.days


def dayForecast(degree, endDate):
    dateList = [endDate.year, endDate.month, endDate.day]

    dayPrediction = "Day Prediction"
    if not os.path.exists(dayPrediction):
        os.mkdir(dayPrediction)

    saveTitle = generateDate(dateList, 0)
    f = open(dayPrediction + "/" + saveTitle, "w")

    root = Tk(className=" COVID-19 " + generateDate(dateList, 0))
    T = Text(root, background="aqua")

    for i in range(1, size):
        setSelect(i)
        title, x, y = readCsv()
        y_head, lr2, pr = ml(x, y, degree)

        begin = countryDate[i - 1]
        diff = dateCompress(begin, endDate, 0) + 1
        guess = math.ceil(predict(lr2, pr, diff))

        information = title + ": " + str(guess) + " (Day -" + str(diff) + "-)" + "\n"
        f.write(information)

        if i % 2 != 0:
            T.insert(INSERT, information, "case")
        else:
            T.insert(INSERT, information, "death")
        T.pack()

    f.close()

    T.tag_config("case", foreground="navy")
    T.tag_config("death", foreground="red")


def countryForecast(degree, end):
    title, x, y = readCsv()
    y_head, lr2, pr = ml(x, y, degree)

    countryPrediction = "Country Prediction"
    if not os.path.exists(countryPrediction):
        os.mkdir(countryPrediction)

    saveTitle = title.replace(" ", "_").lower() + ".txt"
    f = open(countryPrediction + "/" + saveTitle, "w")

    root = Tk(className=" COVID-19 " + title)
    if select % 2 != 0:
        T = Text(root, background="aqua", foreground="navy")
    else:
        T = Text(root, background="aqua", foreground="red")

    begin = countryDate[select - 1]
    dateList = [2020, begin[0], begin[1]]

    first = math.ceil(predict(lr2, pr, 1))
    if first < 0:
        first = 0

    guess = [first]

    information = generateDate(dateList, 0) + " : " + str(guess[0]) + " (Day-1)\n"
    f.write(information)
    T.insert(INSERT, information)

    dayCount = 1
    i = 2
    while dayCount > 0:
        guess.append(math.ceil(predict(lr2, pr, i)))
        if guess[i - 1] < guess[i - 2]:
            guess[i - 1] = guess[i - 2]
        diff = guess[i - 1] - guess[i - 2]

        information = generateDate(dateList, i - 1) + " : " + str(guess[i - 1])
        information += " (Day-" + str(i) + " +" + str(diff) + ")\n"
        f.write(information)
        T.insert(INSERT, information)
        T.pack()

        dayCount = dateCompress(begin, end, i - 1)
        i += 1

    f.close()


def selection():
    colors = ["orange", "blue", "red", "green", "black", "navy"]

    root = Tk(className=" COVID-19 " + getChoose(choose))

    index = 1
    for country in countryList:
        button = Button(root, text=country, bg="aqua", fg=colors[index % len(colors)], width=100,
                        command=lambda value=index: setCountrySelect(value))
        button.pack()
        index += 1
    root.mainloop()

    root = Tk(className=" COVID-19 " + countryList[countrySelect - 1])
    Button(root, text="Case", bg="aqua", fg="navy", width=75,
           command=lambda: setCaseSelect(1)).pack()
    Button(root, text="Death", bg="aqua", fg="red", width=75,
           command=lambda: setCaseSelect(2)).pack()
    root.mainloop()

    setSelect(countrySelect * 2 + caseSelect - 2)


def getChoose(value):
    menuName = ""
    if value == 1:
        menuName = "Graph"
    elif value == 2:
        menuName = "Day Prediction"
    elif value == 3:
        menuName = "Country Prediction"
    elif value == 4:
        menuName = "Exit"
    return menuName


def menu():
    while True:
        root = Tk(className=" COVID-19 Menu")

        Button(root, text=getChoose(1).upper(), bg="aqua", fg="purple", width=75,
               command=lambda: setChoose(1)).pack()
        Button(root, text=getChoose(2).upper(), bg="aqua", fg="navy", width=75,
               command=lambda: setChoose(2)).pack()
        Button(root, text=getChoose(3).upper(), bg="aqua", fg="red", width=75,
               command=lambda: setChoose(3)).pack()
        Button(root, text=getChoose(4).upper(), bg="aqua", fg="black", width=75,
               command=lambda: setChoose(4)).pack()
        root.mainloop()

        if choose == 4:
            messagebox.showwarning("I Hope You Are Fine :)", "Stay at Home!")
            break

        root = Tk(className=" COVID-19 " + getChoose(choose))
        degree = IntVar(root, value=4)
        L1 = Label(root, text="Degree ", bg="aqua", fg="navy", width=25)
        L1.pack(side=LEFT)
        E1 = Entry(root, textvariable=degree, bg="aqua", fg="red", width=25)
        E1.pack(side=RIGHT)
        root.mainloop()

        if choose in (1, 3):
            selection()

        endDate = "13.03.1996"
        if choose in (2, 3):
            root = Tk(className=" COVID-19 " + getChoose(choose))
            today = datetime.today()
            end = StringVar(root, value="{0}.{1}".format(today.day, today.month))
            L1 = Label(root, text="Date ", bg="cyan", fg="navy", width=25)
            L1.pack(side=LEFT)
            E1 = Entry(root, textvariable=end, bg="cyan", fg="red", width=25)
            E1.pack(side=RIGHT)
            root.mainloop()

            end.set(end.get() + ".2020")
            endDate = datetime.strptime(end.get(), '%d.%m.%Y').date()

        if choose == 1:
            plot(degree.get())
        elif choose == 2:
            dayForecast(degree.get(), endDate)
        elif choose == 3:
            countryForecast(degree.get(), endDate)


menu()
