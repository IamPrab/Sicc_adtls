import argparse
import csv
import os
import Utils
import numpy
import xlsxwriter

def FitLinesSICCFactory (outputPath, datafromCsvDIct):

    pairs = Utils.CorrelationValues(datafromCsvDIct)

    #pairs = Utils.createPairs(datafromCsvDIct)
    print('Pairs Created')

    pairFits = Utils.CalFits(pairs, datafromCsvDIct)
    print('Fits Calculated')

    OutPutApproval = Utils.WriteTOApprovalFile(pairFits, outputPath)
    print('Writing Approval File')

    return OutPutApproval

def ReadData (path):
    subfolders_site = [f.path for f in os.scandir(path) if f.is_dir()]

    datafromCsvDIct = {}

    for site in subfolders_site:
        datafiles = os.listdir(site)
        for i in range(len(datafiles)):
            datafiles[i] = os.path.join(site, datafiles[i])

        datafromCsvDIct = Utils.readcsvSICC(datafiles)

    print('DataFiles read')

    return datafromCsvDIct

def DrawGraphs (datafromCsvDIct, outputPath):
    print(outputPath)
    approvalFile = outputPath + "\\SICCApproval.xlsx"
    print(approvalFile)
    approvalFileData = Utils.ReadApprovalFile(approvalFile)

    Utils.GraphFactory(approvalFileData, datafromCsvDIct, outputPath)




parser = argparse.ArgumentParser()

parser.add_argument('operation', help="SiccFit/SiccGraphs")
parser.add_argument('input',help="inputFile")
parser.add_argument('output',help="outputFile")

args = parser.parse_args()

path = args.input
outputPath = args.output

print('Reading dataFiles')
datafromCsvDIct = ReadData(path)

if args.operation == 'SiccFit':
    OutPutApproval = FitLinesSICCFactory(outputPath, datafromCsvDIct)

if args.operation == 'SiccGraphs':
    DrawGraphs(datafromCsvDIct, outputPath)














