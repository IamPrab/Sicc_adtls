import argparse
import csv
import os
import Utils
import numpy
import xlsxwriter


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


def FitLinesSICCFactory (outputPath, datafromCsvDIct):

    #pairs = Utils.CorrelationValues(datafromCsvDIct)

    pairs = Utils.createPairs(datafromCsvDIct)
    print('Pairs Created')

    pairFits = Utils.CalFits(pairs, datafromCsvDIct)
    print('Fits Calculated')

    OutPutApproval = Utils.WriteTOApprovalFile(pairFits, outputPath)
    print('Writing Approval File')

    return OutPutApproval



def DrawGraphs (datafromCsvDIct, outputPath):
    print(outputPath)
    approvalFile = outputPath + "\\SICCApproval.xlsx"
    print(approvalFile)
    approvalFileData = Utils.ReadApprovalFile(approvalFile)

    Utils.GraphFactory(approvalFileData, datafromCsvDIct, outputPath)


def LimitsSICCFactory ( datafromCsvDIct, outputPath):

    existing_limits = Utils.ReadOldData(outputPath)
    siccLimits = Utils.GetBasicParams(datafromCsvDIct, outputPath, existing_limits)
    print("Limits Calculated")
    Utils.WriteToFile(siccLimits, outputPath, existing_limits)

    return

def SiccIdvFitLines(datafromCsvDIct, outputPath):

    idv_data = Utils.GetIdvNameAndData(datafromCsvDIct)

    pairs = Utils.get_idv_sicc_pairs(datafromCsvDIct, idv_data)

    pairFits = Utils.CalFits(pairs, datafromCsvDIct)
    print('Fits Calculated')

    OutPutApproval = Utils.WriteTOApprovalFile(pairFits, outputPath)
    print('Writing Approval File')

    return OutPutApproval

    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('operation', help="SiccFit/SiccGraphs/SiccIdvFits")
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

    if args.operation == 'SiccLimits':
        LimitsSICCFactory(datafromCsvDIct,outputPath)

    if args.operation == 'SiccIdvFits':
        SiccIdvFitLines(datafromCsvDIct, outputPath)














