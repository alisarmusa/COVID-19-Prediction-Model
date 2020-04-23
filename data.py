import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import date, timedelta
from time import strptime


def convertDate(dateList):
    month = strptime(dateList[0], '%b').tm_mon
    day = int(dateList[1])
    beginDate = [month, day]
    return beginDate


def generateDate(startDate, number):
    d = date(2020, startDate[0], startDate[1]) + timedelta(days=number)
    return str(d.strftime('%b%d'))


def getCountryList(url):
    result = requests.get(url)
    src = result.content
    soup = BeautifulSoup(src, 'html.parser')

    nameList = []
    hrefList = []
    for a in soup.find_all("a", class_='mt_a'):
        nameList.append(a.text)
        hrefList.append(a['href'])
    # Return Top 10 Countries
    return nameList[:10], hrefList[:10]


def getCountryData(url, case):
    result = requests.get(url)
    src = result.content
    soup = BeautifulSoup(src, 'html.parser')

    dataScript = ""
    for script in soup.find_all("script"):
        if case in script.text:
            dataScript = script.text
            break

    dateList = dataScript.split('categories: [', 1)[1].split(']', 1)[0].replace('"', '').split(",")

    data = dataScript.split('data: [', 1)[1].split(']', 1)[0].split(",")
    data = [int(d) for d in data]

    index = 0
    for d in range(0, len(data)):
        if data[d] > 0:
            index = d
            break

    beginDate = convertDate(dateList[index].split(" "))

    return data[index:], beginDate


def getDataList():
    dataList = []
    dateList = []
    url = "https://www.worldometers.info/coronavirus/"

    data, dateWorld = getCountryData(url, "Total Cases")
    dataList.append(data)
    dateList.append(dateWorld)

    data, dateWorld = getCountryData(url, "Total Deaths")
    dataList.append(data)
    dateList.append(dateWorld)

    countryList, hrefList = getCountryList(url)

    for href in hrefList:
        countryUrl = url + href

        data, dateCountry = getCountryData(countryUrl, "Total Cases")
        dataList.append(data)
        dateList.append(dateCountry)

        data, dateCountry = getCountryData(countryUrl, "Total Deaths")
        dataList.append(data)
        dateList.append(dateCountry)

    countryList.insert(0, "World")
    return countryList, dataList, dateList


def generateData():
    countryList, dataList, dateList = getDataList()

    countries = "Countries"

    if not os.path.exists(countries):
        os.mkdir(countries)

    for country in countryList:
        if not os.path.exists(countries + "/" + country):
            os.mkdir(countries + "/" + country)

    countryCount = 0
    dateCount = 0
    flag = True
    for data in dataList:
        if flag:
            doc = countries + "/" + countryList[countryCount] + "/case.csv"
            flag = False
        else:
            doc = countries + "/" + countryList[countryCount] + "/death.csv"
            flag = True
        with open(doc, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["day", "dayNo", "case"])
            i = 1
            for case in data:
                writer.writerow([generateDate(dateList[dateCount], i - 1), i, case])
                i += 1
        dateCount += 1
        if flag:
            countryCount += 1

    return countryList, dateList
