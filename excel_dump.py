import re
from openpyxl import load_workbook
import json
import os
from pprint import pprint
import xlwt



def excelDump(data, book, sheetname):

    sheet = book.add_sheet(sheetname)
    sheet.write(0, 0, "Title")
    sheet.write(0, 1, "Desc")
    sheet.write(0, 2, "Address")
    sheet.write(0, 3, "Telephone")
    sheet.write(0, 4, "Keywords")

    count = 1

    if data:
        #for i in range(0, len(data[0])):
        for i in range(0, len(data)):

            if data[i]["desc"] == None:
                data[i]["desc"] = ''

            if data[i]["address"] == None:
                data[i]["address"] = ''

            if data[i]["telephone"] == None:
                data[i]["telephone"] = ''

            if data[i]["keywords"] == None:
                data[i]["keywords"] = ''

            data[i]["title"] = str(data[i]["title"])
            data[i]["desc"] = str(data[i]["desc"])
            data[i]["telephone"] = str(data[i]["telephone"])
            data[i]["address"] = str(data[i]["address"])
            data[i]["keywords"] = str(data[i]["keywords"])
            data[i]["address"] = re.sub(r'\t*', '',data[i]["address"])
            data[i]["address"] = re.sub(r'\n*', '',data[i]["address"])
            data[i]["title"] = re.sub(r'\t*', '',data[i]["title"])
            data[i]["title"] = re.sub(r'\n*', '',data[i]["title"])
            data[i]["desc"] = re.sub(r'\t*', '',data[i]["desc"])
            data[i]["desc"] = re.sub(r'\n*', '',data[i]["desc"])
            data[i]["telephone"] = re.sub(r'\t*', '',data[i]["telephone"])
            data[i]["telephone"] = re.sub(r'\n*', '',data[i]["telephone"])
            data[i]["keywords"] = re.sub(r'\t*', '',data[i]["keywords"])
            data[i]["keywords"] = re.sub(r'\n*', '',data[i]["keywords"])
            data[i]["title"] = data[i]["title"].split(r' - ', 1)[0]

            data[i]["desc"] = re.sub('  +',' ',data[i]["desc"])
            data[i]["address"] = re.sub('  +',' ',data[i]["address"])
            data[i]["telephone"] = re.sub('  +',' ',data[i]["telephone"])

#This Part Removes weird error but introduces inverted commas
            #data[i]["title"] = re.sub(r'\\u....', '',ascii(data[i]["title"]))
            #data[i]["title"] = ascii(data[i]["title"])
            data[i]["desc"] = re.sub(r'\\u....', '',ascii(data[i]["desc"]))
            data[i]["address"] = re.sub(r'\\u....', '',ascii(data[i]["address"]))
            data[i]["telephone"] = re.sub(r'\\u....', '',ascii(data[i]["telephone"]))
            data[i]["keywords"] = re.sub(r'\\u....', '',ascii(data[i]["keywords"]))

            ###Don't print duplicates
            writetofile = 1
            #print(data[i]["title"] + "  " + data[i]["address"])
            for x in range(0,i):
                if data[i]["title"] == data[x]["title"] and data[i]["address"] == data[x]["address"]:
                    writetofile = 0
                    #print("match: " + data[i]["title"])

            if writetofile == 1:
                sheet.write(count, 0, data[i]["title"])#[1:-1])
                sheet.write(count, 1, data[i]["desc"][1:-1])
                sheet.write(count, 2, data[i]["address"][1:-1])
                sheet.write(count, 3, data[i]["telephone"][1:-1])
                sheet.write(count, 4, data[i]["keywords"][1:-1])

                count = count + 1

            if i == 1000:
                print(data[i]["title"])
                print(data[i]["desc"])


def serviceCategorise():

    Website = "yelp"
    City = "taipei"

    book = xlwt.Workbook()

    fitnessText = ""
    groomingText = ""
    localText = ""
    styleText = ""
    technicalText = ""
    wellnessText = ""

    fitnessNonMatch = []
    groomingNonMatch = []
    localNonMatch = []
    styleNonMatch = []
    technicalNonMatch = []
    wellnessNonMatch = []

    fitcount = 1
    groomcount = 1
    localcount = 1
    stylecount = 1
    technicalcount = 1
    wellnesscount = 1

    #Read in json file
    def readFile(category):

        if os.path.exists('Websites/' + Website + "_" + City + "/" + Website + "_" + category + ".json"):
            print("HOLAAAA")

            with open(r'Websites/' + Website + "_" + City + "/" + Website + "_" + category + ".json", encoding='utf-8') as data_file:
                data = json.loads(data_file.read())

            data_file.close()

            return data

    # data = readFile("Fitness")
    # excelDump(data, book, "Fitness")
    # del data[:]
    # data = readFile("Wellness")
    # excelDump(data, book, "Wellness")
    # del data[:]
    # data = readFile("Grooming")
    # excelDump(data, book, "Grooming")
    # del data[:]
    data = readFile("Local")
    excelDump(data, book, "Local")
    del data[:]
    data = readFile("Style")
    excelDump(data, book, "Style")
    del data[:]
    data = readFile("Technical")
    excelDump(data, book, "Technical")


    book.save("Websites/" + Website + "_" + City + "/" + Website + "_scrape.xls")




serviceCategorise()