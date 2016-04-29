from negex import *
import csv
from file_formatting import format_file
import numpy

##*********Should give each review a maximum category value contribution?

def category_mf(keyword, negation_status, MFList, descriptCategories):

    print(keyword)
    print(negation_status)
    print(MFList)
    MFList = numpy.matrix(MFList)

    #polarity = numpy.empty(len(negation_status), dtype=int)

    for i in range (0, len(negation_status)):      #Do all in matrices

        if negation_status[i] == "negated":

            MFList[i] = -1 * MFList[i]

        MFSum = numpy.sum(MFList, axis=0)
        MFSum = numpy.array(MFSum)

    print(MFList)
    print("MF Sum: ")
    print(MFSum)

    print("\n")
    print("Service Provider Fits Keywords: " )
    for col in  range (0, len(descriptCategories)):

        if MFSum[0][col] > 1:
            print(descriptCategories[col])

    print("\n")
    print("Service Provider Does Not Fit Keywords: " )
    for col in  range (0, len(descriptCategories)):

        if MFSum[0][col] < 0.1:
            print(descriptCategories[col])


def main():

    rfile = open(r'Input Files/negex_triggers.txt')
    irules = sortRules(rfile.readlines())
    #reports = csv.reader(open(r'Annotations-1-120.txt','r'), delimiter = '\t')
    #reports = csv.reader(open(r'review_text.txt','r'), delimiter = '\t')
    reports = csv.reader(open(r'negex_in.txt','r'), delimiter = '\t')

    categoryMatrix = []     #Sum the MFs to each category

    reports.__next__()
    reportNum = 0
    correctNum = 0
    ofile = open(r'negex_output.txt', 'w')
    output = []
    outputfile = csv.writer(ofile, delimiter = '\t')

    MFList, descriptCategories = format_file()
    NegFlagList = []
    KeywordList = []

    for report in reports:

        #print(report)
        tagger = negTagger(sentence = report[2], phrases = [report[1]], rules = irules, negP=False)
        report.append(tagger.getNegTaggedSentence())
        report.append(tagger.getNegationFlag())
        report = report + tagger.getScopes()
        reportNum += 1
        if report[3].lower() == report[5]:
            correctNum += 1
        output.append(report)

        NegFlagList = NegFlagList + [tagger.getNegationFlag()]
        KeywordList = KeywordList + [report[1]]

        ###Category MF - Phrase -
        #category_mf(report[1], NegFlagList, categoryMatrix)

    category_mf(KeywordList, NegFlagList, MFList, descriptCategories)
    #print(KeywordList)
    outputfile.writerow(['Percentage correct:', float(correctNum)/float(reportNum)])
    for row in output:
        if row:
            outputfile.writerow(row)
    ofile.close()

if __name__ == '__main__': main()

