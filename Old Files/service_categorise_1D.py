import re
from openpyxl import load_workbook
import json
import os
from pprint import pprint
import xlwt


def serviceCategorise():

    #Website = "smartshanghai_tailor_items"
    Website = "smartshanghai_wellness_items"
    #Website = "urbanlist_sydney"
    #Website = "findyoga_items"



    book = xlwt.Workbook()
    Fitness = book.add_sheet("Fitness")
    Grooming = book.add_sheet("Grooming")
    Local = book.add_sheet("Local")
    Style = book.add_sheet("Style")
    Technical = book.add_sheet("Technical")
    Wellness = book.add_sheet("Wellness")

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

    Fitness.write(0, 0, "Title")
    Fitness.write(0, 1, "Desc")
    Fitness.write(0, 2, "Address")
    Fitness.write(0, 3, "Telephone")
    Grooming.write(0, 0, "Title")
    Grooming.write(0, 1, "Desc")
    Grooming.write(0, 2, "Address")
    Grooming.write(0, 3, "Telephone")
    Local.write(0, 0, "Title")
    Local.write(0, 1, "Desc")
    Local.write(0, 2, "Address")
    Local.write(0, 3, "Telephone")
    Style.write(0, 0, "Title")
    Style.write(0, 1, "Desc")
    Style.write(0, 2, "Address")
    Style.write(0, 3, "Telephone")
    Technical.write(0, 0, "Title")
    Technical.write(0, 1, "Desc")
    Technical.write(0, 2, "Address")
    Technical.write(0, 3, "Telephone")
    Wellness.write(0, 0, "Title")
    Wellness.write(0, 1, "Desc")
    Wellness.write(0, 2, "Address")
    Wellness.write(0, 3, "Telephone")


    #Reading in category files
    fitnessFile = open(r'Keywords/Fitness Services.txt', 'r')
    fitnessFile = fitnessFile.read()
    fitnessFile = str.split(str(fitnessFile), '\n')

    groomingFile = open(r'Keywords/Grooming Services.txt', 'r')
    groomingFile = groomingFile.read()
    groomingFile = str.split(str(groomingFile), '\n')

    localFile = open(r'Keywords/Local Services.txt', 'r')
    localFile = localFile.read()
    localFile = str.split(str(localFile), '\n')

    styleFile = open(r'Keywords/Style Services.txt', 'r')
    styleFile = styleFile.read()
    styleFile = str.split(str(styleFile), '\n')

    technicalFile = open(r'Keywords/Technical Services.txt', 'r')
    technicalFile = technicalFile.read()
    technicalFile = str.split(str(technicalFile), '\n')

    wellnessFile = open(r'Keywords/Wellness Services.txt', 'r')
    wellnessFile = wellnessFile.read()
    wellnessFile = str.split(str(wellnessFile), '\n')

    #undesiredList = ["food", "cafe", "coffee", "espresso", "baked", "bakery", "flavour"]
    undesiredList = ["FOOD", "CAFE", "COFFEE", "ESPRESSO", "BAKED", "BAKERY", "FLAVOUR", \
                     "FLAVOURS", "BAR", "FLORIST", "FLOWER", "FLORAL", "DINING", "PUB", \
                    "MENU", "BEER" "MEAT", "BREAKFAST", "CUISINE", "GOURMET", "LIVE MUSIC", \
                     "SHOP", "BOOKSHOP", "BOOK", "BOOKSTORE", "SEAFOOD", "CAFE�", "PIE", \
                     "PASTRY", "RESTAURANT", "PASTA", "ITALIAN FOOD", "STORE", "SHOP", "SHOPPING",\
                     "BURGER", "CHOCOLATE", "WHISKEY", "EATERY", "DRINKS", "DRINKING", "BICYCLE", \
                     "BIKE", "RETAILER", "FURNITURE", "EYEWEAR", "GLASSES", "JUICE"]


    #Read in json file
    with open(r"Websites/" + Website + ".json", encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
        #data = data_file.read()

    data_file.close()

    #for i in range(0, len(data[0])):
    for i in range(0, len(data)):

        if data[i]["desc"] == None:
            data[i]["desc"] = ''

        if data[i]["address"] == None:
            data[i]["desc"] = ''

        #Remove apostrophies -  necessary??
        data[i]["desc"] = re.sub(r'\'', '',data[i]["desc"])

        for word in fitnessFile:

            #mid sentence word
            #before full stop word
            #before comma word
            if word + ' ' in data[i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[i]["desc"])

                Fitness.write(fitcount, 0, data[i]["title"])
                Fitness.write(fitcount, 1, data[i]["desc"])
                Fitness.write(fitcount, 2, data[i]["address"])
                Fitness.write(fitcount, 3, data[i]["telephone"])
                fitcount = fitcount + 1

                #fitnessText = fitnessText + data[i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[i]["address"] + "\n"
                #fitnessText = fitnessText + data[0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][i]["address"] + "\n"
                breakflag = 1
                break

            breakflag = 0

        if breakflag == 0:
            fitnessNonMatch = fitnessNonMatch + [i]


        for word in groomingFile:

            if word + ' ' in data[i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[i]["desc"])

                Grooming.write(groomcount, 0, data[i]["title"])
                Grooming.write(groomcount, 1, data[i]["desc"])
                Grooming.write(groomcount, 2, data[i]["address"])
                Grooming.write(groomcount, 3, data[i]["telephone"])
                groomcount = groomcount + 1

                #groomingText = groomingText + data[i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[i]["address"] + "\n"
                #groomingText = groomingText + data[0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][i]["address"] + "\n"
                breakflag = 1
                break

            breakflag = 0

        if breakflag == 0:
            groomingNonMatch = groomingNonMatch + [i]

        for word in localFile:

            if word + ' ' in data[i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[i]["desc"])

                Local.write(localcount, 0, data[i]["title"])
                Local.write(localcount, 1, data[i]["desc"])
                Local.write(localcount, 2, data[i]["address"])
                Local.write(localcount, 3, data[i]["telephone"])
                localcount = localcount + 1

                #localText = localText + data[i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[i]["address"] + "\n"
                #localText = localText + data[0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][i]["address"] + "\n"
                breakflag = 1
                break

            breakflag = 0

        if breakflag == 0:
            localNonMatch = localNonMatch + [i]

        for word in styleFile:

            if word + ' ' in data[i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[i]["desc"])

                Style.write(stylecount, 0, data[i]["title"])
                Style.write(stylecount, 1, data[i]["desc"])
                Style.write(stylecount, 2, data[i]["address"])
                Style.write(stylecount, 3, data[i]["telephone"])
                stylecount = stylecount + 1

                #styleText = styleText + data[i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[i]["address"] + "\n"
                #styleText = styleText + data["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][i]["address"] + "\n"
                breakflag = 1
                break

            breakflag = 0

        if breakflag == 0:
            styleNonMatch = styleNonMatch + [i]

        for word in technicalFile:

            if word + ' ' in data[i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[i]["desc"])

                Technical.write(technicalcount, 0, data[i]["title"])
                Technical.write(technicalcount, 1, data[i]["desc"])
                Technical.write(technicalcount, 2, data[i]["address"])
                Technical.write(technicalcount, 3, data[i]["telephone"])
                technicalcount = technicalcount + 1

                #technicalText = technicalText + data[i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[i]["address"] + "\n"
                #technicalText = technicalText + data[0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][i]["address"] + "\n"
                breakflag = 1
                break

            breakflag = 0

        if breakflag == 0:
            technicalNonMatch = technicalNonMatch + [i]


        for word in wellnessFile:

            if word + ' ' in data[i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[i]["desc"])

                Wellness.write(wellnesscount, 0, data[i]["title"])
                Wellness.write(wellnesscount, 1, data[i]["desc"])
                Wellness.write(wellnesscount, 2, data[i]["address"])
                Wellness.write(wellnesscount, 3, data[i]["telephone"])
                wellnesscount = wellnesscount + 1

                #wellnessText = wellnessText + data[i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[i]["address"] + "\n"
                #wellnessText = wellnessText + data[0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][i]["address"] + "\n"
                breakflag = 1
                break

            breakflag = 0

        if breakflag == 0:
            wellnessNonMatch = wellnessNonMatch + [i]


    if not os.path.exists('Websites/' + Website):
        os.makedirs('Websites/' + Website)

    f = open('Websites/' + Website + '/Fitness_SPs.txt','w')
    f.write(fitnessText)
    f.close()

    f = open('Websites/' + Website + '/Grooming_SPs.txt','w')
    f.write(groomingText)
    f.close()

    f = open('Websites/' + Website + '/Local_SPs.txt','w')
    f.write(localText)
    f.close()

    f = open('Websites/' + Website + '/Style_SPs.txt','w')
    f.write(styleText)
    f.close()

    f = open('Websites/' + Website + '/Technical_SPs.txt','w')
    f.write(technicalText)
    f.close()

    f = open('Websites/' + Website + '/Wellness_SPs.txt','w')
    f.write(wellnessText)
    f.close()

    book.save("Excel.xls")

    #Fitness.write(0, 0, 'foobar') # row, column, value
    #print(localText)

    ##Finding uncategorised SPs
    #print(list(set(a) & set(b))

    nonmatchlist = list(set(fitnessNonMatch) & set(groomingNonMatch) & set(localNonMatch) & set(styleNonMatch) & set(technicalNonMatch) & set(wellnessNonMatch))
    f = open('Websites/' + Website + '/Uncategorised_SPs.txt','w')
    #print(groomingNonMatch)



    undesired = 0
    for elem in nonmatchlist:

     ##Remove restaurants and cafes from undesired list
        for word in undesiredList:

            #if word in data[elem]["desc"]:
            if word + ' ' in data[elem]["desc"]\
                    or ' ' + word.upper() + ' ' in data[elem]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[elem]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[elem]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[elem]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[elem]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[elem]["desc"].upper():
                undesired = 1

        if undesired == 0:
            #print(data[elem]["title"])
            f.write(data[elem]["title"] + "\n" + data[elem]["desc"] + "\n\n")
            #f.write(data[elem]["title"])

        undesired = 0

    f.close()


serviceCategorise()