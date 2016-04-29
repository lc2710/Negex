import re
from openpyxl import load_workbook
import json
import os
from pprint import pprint


def serviceCategorise():

    Website = "urbanlist_sydney"
    #Website = "findyoga_items"

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

    data_file.close()


    #myfile = re.sub(r'\",', '',myfile)

    #for i in range(0, len(data[0])):
    for i in range(0, len(data[0][0])):

        #Remove apostrophies -  necessary??
        data[0][0][i]["desc"] = re.sub(r'\'', '',data[0][0][i]["desc"])

        for word in fitnessFile:

            #mid sentence word
            #before full stop word
            #before comma word
            if word + ' ' in data[0][0][i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[0][0][i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[0][0][i]["desc"])

                fitnessText = fitnessText + data[0][0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][0][i]["address"] + "\n"
                #fitnessText = fitnessText + data[0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][i]["address"] + "\n"
                breakflag = 1
                break

            breakflag = 0

        if breakflag == 0:
            fitnessNonMatch = fitnessNonMatch + [i]


        for word in groomingFile:

            if word + ' ' in data[0][0][i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[0][0][i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[0][0][i]["desc"])

                groomingText = groomingText + data[0][0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][0][i]["address"] + "\n"
                #groomingText = groomingText + data[0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][i]["address"] + "\n"
                breakflag = 1
                break

            breakflag = 0

        if breakflag == 0:
            groomingNonMatch = groomingNonMatch + [i]

        for word in localFile:

            if word + ' ' in data[0][0][i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[0][0][i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[0][0][i]["desc"])

                localText = localText + data[0][0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][0][i]["address"] + "\n"
                #localText = localText + data[0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][i]["address"] + "\n"
                breakflag = 1
                break

            breakflag = 0

        if breakflag == 0:
            localNonMatch = localNonMatch + [i]

        for word in styleFile:

            if word + ' ' in data[0][0][i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[0][0][i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[0][0][i]["desc"])


                styleText = styleText + data[0][0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][0][i]["address"] + "\n"
                #styleText = styleText + data[0][0]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][i]["address"] + "\n"
                breakflag = 1
                break

            breakflag = 0

        if breakflag == 0:
            styleNonMatch = styleNonMatch + [i]

        for word in technicalFile:

            if word + ' ' in data[0][0][i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[0][0][i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[0][0][i]["desc"])

                technicalText = technicalText + data[0][0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][0][i]["address"] + "\n"
                #technicalText = technicalText + data[0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][i]["address"] + "\n"
                breakflag = 1
                break

            breakflag = 0

        if breakflag == 0:
            technicalNonMatch = technicalNonMatch + [i]


        for word in wellnessFile:

            if word + ' ' in data[0][0][i]["desc"] + ' ' \
                    or ' ' + word.upper() + ' ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[0][0][i]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[0][0][i]["desc"].upper():

                if word.upper() in undesiredList:
                    print("Possible undesirable: " + word + "   " + data[0][0][i]["desc"])


                wellnessText = wellnessText + data[0][0][i]["title"] + "\t\t\t\t\t\t\t\tAddress: " + data[0][0][i]["address"] + "\n"
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

    ##Finding uncategorised SPs
    #print(list(set(a) & set(b))

    nonmatchlist = list(set(fitnessNonMatch) & set(groomingNonMatch) & set(localNonMatch) & set(styleNonMatch) & set(technicalNonMatch) & set(wellnessNonMatch))
    f = open('Websites/' + Website + '/Uncategorised_SPs.txt','w')
    #print(groomingNonMatch)



    undesired = 0
    for elem in nonmatchlist:

     ##Remove restaurants and cafes from undesired list
        for word in undesiredList:

            #if word in data[0][0][elem]["desc"]:
            if word + ' ' in data[0][0][elem]["desc"]\
                    or ' ' + word.upper() + ' ' in data[0][0][elem]["desc"].upper()\
                    or ' ' + word.upper() + '.' in data[0][0][elem]["desc"].upper()\
                    or ' ' + word.upper() + ',' in data[0][0][elem]["desc"].upper()\
                    or ' ' + word.upper() + 'S ' in data[0][0][elem]["desc"].upper()\
                    or ' ' + word.upper() + 'S.' in data[0][0][elem]["desc"].upper()\
                    or ' ' + word.upper() + 'S,' in data[0][0][elem]["desc"].upper():
                undesired = 1

        if undesired == 0:
            print(data[0][0][elem]["title"])
            f.write(data[0][0][elem]["title"] + "\n" + data[0][0][elem]["desc"] + "\n\n")
            #f.write(data[0][0][elem]["title"])

        undesired = 0

    f.close()


serviceCategorise()