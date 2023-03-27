import gc
import math
import os
import csv
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from numpy.polynomial.polynomial import polyfit
import xlsxwriter
from scipy.stats import pearsonr

Pairs ={
    'VMIN': 'VMAX'
}

def readcsvSICC(datafiles):

    datadictFromCSV = {}
    for datafile in datafiles:
        fileopen = open(datafile)
        data = csv.DictReader(fileopen)

        for row in data:
            testname = row['test']
            lot = row['Lot']
            waferId = row['Wafer_ID']
            x = row['X']
            y = row['Y']
            ibin = row['IB']
            result = float(row['result'])

            uniqueID = lot + "%" + waferId + "%" + x + "%" + y + "%" + ibin
            if testname not in datadictFromCSV:
                datadictFromCSV[testname] = [[result],[uniqueID]]
            else:
                resultList = datadictFromCSV[testname][0]
                uniqueIDList = datadictFromCSV[testname][1]

                resultList.append(result)
                uniqueIDList.append(uniqueID)

                datadictFromCSV[testname] = [resultList,uniqueIDList]


    return datadictFromCSV

def get_x_y_pair(data_instance_x, data_instance_y):
    x_len = len(data_instance_x[0])
    y_len = len(data_instance_y[0])
    x=[]
    y=[]
    refernce_unit = []
    if x_len<=y_len:
        refernce_unit = data_instance_x[1]
    else:
        refernce_unit = data_instance_y[1]

    for val in refernce_unit:
        if val in data_instance_x[1]:
            if val in data_instance_y[1]:
                x_val = data_instance_x[0][data_instance_x[1].index(val)]
                y_val = data_instance_y[0][data_instance_y[1].index(val)]

                x.append(x_val)
                y.append(y_val)

    return x,y


def CorrelationValues(datafromCsvDIct):
    correlationMatrix = {}
    DuplicateCheck = {}

    with open('Correlation_Val.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["VminTest 1", "Group1", "Vmintest 2", "group 2", "Correlation cofficeint"])
        for test_x in datafromCsvDIct:
            correlationVmin = test_x

            for test_y in datafromCsvDIct:
                key2 = test_x + '@' + test_y
                if key2 not in DuplicateCheck:
                    if test_y != correlationVmin:
                        x1 = datafromCsvDIct[correlationVmin]
                        x2 = datafromCsvDIct[test_y]

                        x1,x2 = get_x_y_pair(x1,x2)

                        key = test_x + '@' + test_y
                        DuplicateCheck[key] = True
                        if len(x1)!=len(x2):
                            print(len(x1),len(x2))
                            print(test_y,test_x)

                        correlation, p_value = pearsonr(x1, x2)

                        if correlation > 0.8 or correlation < -0.8:
                            correlationMatrix[key] = correlation
                            rowData = [correlationVmin, test_y,
                                       correlation]
                            writer.writerow(rowData)
                            print(correlation)

    return correlationMatrix



def createPairs(dictData):

    pairsofTests = []

    for testname in dictData:
        for pair in Pairs:
            if testname.find(pair)>0:
                pairTest =  testname.replace(pair, Pairs[pair])

                pairToGo = [testname,pairTest]
                pairsofTests.append(pairToGo)


    return pairsofTests

def getLinePoints(x, y, b, m):
    c = 0
    linePoints = []
    while (c < len(x)):
        z = m * x[c] + b
        linePoints.append(z)
        c = c + 1
    return linePoints

def GetFitLines(x, y):

    b, m = polyfit(x, y, 1)
    linePoints = getLinePoints(x, y, b, m)
    MSE = np.square(np.subtract(y, linePoints)).mean()
    RMSE = math.sqrt(MSE)

    return [m,b,RMSE]

def CalFits(pairs, datafromCsvDIct):
    pairFits = {}
    for pair in pairs:
        x_y = pair.split('@')
        x, y = get_x_y_pair(datafromCsvDIct[x_y[0]], datafromCsvDIct[x_y[1]])
        fit = GetFitLines(x, y)
        key = pair[0] + "%" + pair[1]

        pairFits[key] = fit

    return pairFits

def WriteTOApprovalFile (pairFits, path):
    OutFinalCSVPath = path + "\\SICCApproval.xlsx"
    workbook = xlsxwriter.Workbook(OutFinalCSVPath)
    worksheet = workbook.add_worksheet()
    header = ['SICC Test X', 'SICC Test Y', 'Slope', 'Intercept', 'RMSE']
    worksheet.write_row(0, 0, header)
    count = 0

    for pairFit in pairFits:
        count = count+1
        names = pairFit.split('%')
        data = pairFits[pairFit]
        row = [names[0], names[1], data[0], data[1], data[2]]
        worksheet.write_row(count,0,row)

        graphName = path + "\\GraphDataSICC\\" + pairFit.split('::')[0] + '_' + str(count) + '.png'
        worksheet.write_url(count,5,graphName)


    workbook.close()
    return OutFinalCSVPath

def ReadApprovalFile(csvAprrovalFile):
    excel_data = pd.read_excel(csvAprrovalFile)
    dict_data = {}
    data = pd.DataFrame(excel_data, columns=['SICC Test X', 'SICC Test Y', 'Slope', 'Intercept', 'RMSE'])
    length = (len(data['SICC Test X']))
    count = 0
    # print(length)
    while (count < length):
        key = data['SICC Test X'][count] + "%" + data['SICC Test Y'][count]
        if key not in dict_data:
            stuff = [data['SICC Test X'][count], (data['SICC Test Y'][count]), float(data['Slope'][count]),
                     float(data['Intercept'][count]), float(data['RMSE'][count]),count]
            dict_data[key] = stuff
        else:
            print(key)
            print("double Equation ^^")
        count = count + 1

    return dict_data

def GraphFactory(approvalFileData, datafromCsvDIct, outputPath):

    for pair in approvalFileData:
        X_name = approvalFileData[pair][0]
        Y_name = approvalFileData[pair][1]
        slope = approvalFileData[pair][2]
        intercept = approvalFileData[pair][3]
        rmse = approvalFileData[pair][4]
        count = approvalFileData[pair][5]

        X_Data = datafromCsvDIct[X_name][0]
        Y_Data = datafromCsvDIct[Y_name][0]

        StoreGraph(X_name, X_Data, Y_name, Y_Data, slope, intercept, rmse, count, outputPath)

    return

def StoreGraph(X_name, X_Data, Y_name, Y_Data, slope, intercept, rmse, count, outputPath):
    results_dir = os.path.join(outputPath + '/GraphDataSICC')
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
        print(results_dir+"...Result directory")

    x = np.array(X_Data)
    y = np.array(Y_Data)

    plt.figure()

    plt.scatter(x, y, marker='^', color='blue', label="Unit")
    plt.xlabel(X_name)
    plt.ylabel(Y_name)
    plt.plot(x, intercept + slope * x, 'g-', label = "FitLine")

    offset = intercept + 6*(rmse)
    plt.plot(x, offset + slope * x, 'r-',label = "KillLine_6_Sigma")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    filename = results_dir + "\\" + str(count+1) +".png"
    if '::' in X_name:
        filename = results_dir + "\\" + X_name.split('::')[0] + '_' + str(count+1) +".png"

    plt.savefig(filename, bbox_inches='tight')
    plt.clf()
    plt.close()
    del x, y
    gc.collect()












