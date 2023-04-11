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
from scipy import stats

Pairs = {
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
                datadictFromCSV[testname] = [[result], [uniqueID]]
            else:
                resultList = datadictFromCSV[testname][0]
                uniqueIDList = datadictFromCSV[testname][1]

                resultList.append(result)
                uniqueIDList.append(uniqueID)

                datadictFromCSV[testname] = [resultList, uniqueIDList]

    return datadictFromCSV


def get_x_y_pair(data_instance_x, data_instance_y):
    x_len = len(data_instance_x[0])
    y_len = len(data_instance_y[0])
    x = []
    y = []
    refernce_unit = []
    if x_len <= y_len:
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

    return x, y


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

                        x1, x2 = get_x_y_pair(x1, x2)

                        key = test_x + '@' + test_y
                        DuplicateCheck[key] = True
                        if len(x1) != len(x2):
                            print(len(x1), len(x2))
                            print(test_y, test_x)

                        correlation, p_value = pearsonr(x1, x2)

                        if correlation > 0.9 or correlation < -0.9:
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
            if testname.find(pair) > 0:
                pairTest = testname.replace(pair, Pairs[pair])

                pairToGo = [testname, pairTest]
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

    return [m, b, RMSE]


def CalFits(pairs, datafromCsvDIct):
    pairFits = {}
    for pair in pairs:
        x_y = pair.split('@')
        x, y = get_x_y_pair(datafromCsvDIct[x_y[0]], datafromCsvDIct[x_y[1]])
        fit = GetFitLines(x, y)

        pairFits[pair] = fit

    return pairFits


def WriteTOApprovalFile(pairFits, path):
    OutFinalCSVPath = path + "\\SICCApproval.xlsx"
    workbook = xlsxwriter.Workbook(OutFinalCSVPath)
    worksheet = workbook.add_worksheet()
    header = ['SICC Test X', 'SICC Test Y', 'Slope', 'Intercept', 'RMSE']
    worksheet.write_row(0, 0, header)
    count = 0

    for pairFit in pairFits:
        count = count + 1
        names = pairFit.split('@')
        data = pairFits[pairFit]
        row = [names[0], names[1], data[0], data[1], data[2]]
        worksheet.write_row(count, 0, row)

        graphName = path + "\\GraphDataSICC\\" + pairFit.split('::')[0] + '_' + str(count) + '.png'
        worksheet.write_url(count, 5, graphName)

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
                     float(data['Intercept'][count]), float(data['RMSE'][count]), count]
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
        slope = float(approvalFileData[pair][2])
        intercept = float(approvalFileData[pair][3])
        rmse = float(approvalFileData[pair][4])
        count = approvalFileData[pair][5]

        X_Data = datafromCsvDIct[X_name]
        Y_Data = datafromCsvDIct[Y_name]

        StoreGraph(X_name, X_Data, Y_name, Y_Data, slope, intercept, rmse, count, outputPath)

    return


def StoreGraph(X_name, X_Data, Y_name, Y_Data, slope, intercept, rmse, count, outputPath):
    results_dir = os.path.join(outputPath + '/GraphDataSICC')

    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
        print(results_dir + "...Result directory")

    x, y = get_x_y_pair(X_Data, Y_Data)
    x = np.array(x)
    y = np.array(y)

    plt.figure()

    plt.scatter(x, y, marker='^', color='blue', label="Unit")
    plt.xlabel(X_name)
    plt.ylabel(Y_name)
    plt.plot(x, float(intercept) + float(slope) * x, 'g-', label="FitLine")

    offset = intercept + 6 * (rmse)
    plt.plot(x, offset + slope * x, 'r-', label="KillLine_6_Sigma")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    filename = results_dir + "\\" + str(count + 1) + ".png"
    if '::' in X_name:
        filename = results_dir + "\\" + X_name.split('::')[0] + '_' + str(count + 1) + ".png"

    plt.savefig(filename, bbox_inches='tight')
    plt.clf()
    plt.close()
    del x, y
    gc.collect()


###########################################################################################################################################################

def ReadOldData(outputPath):
    gsdsTokens = outputPath + "/GSDSTokens.csv"

    tokens_limits = {}
    if os.path.exists(gsdsTokens):
        fileopen = open(gsdsTokens)
        data = csv.DictReader(fileopen)

        for row in data:
            key = row['TestName'] + '_' + row['ItuffToken'].upper()
            tokens_limits[key] = {
                'GSDS': row['GSDSToken'],
                'HighLimit': row['HighLimit'],
                'LowLimit': row['LowLimit'],
                'Pin': row['Pin'],
                'TestName': row['TestName'] + '_' + row['ItuffToken'],
                'ItuffToken': row['ItuffToken'],
                'ConfigFile' : row['ConfigFile'],
                'ConfigSet' : row['ConfigSet']
            }

    return tokens_limits


def WriteToFile(siccLimits, outputPath, existing_limits):
    OutFinalCSVPath = outputPath + "\\SICCApprovalLimits.xlsx"
    workbook = xlsxwriter.Workbook(OutFinalCSVPath)
    worksheet = workbook.add_worksheet()
    header = ['SICC Test', 'Mean', 'Median', 'Standard Deviation', 'PseduSigma_Upper', 'PseduSigma_Lower', 'HighLimit',
              'LowLimit', 'Approval','Graph', 'Previous Low Limit', 'Previous High Limit', 'GSDS', 'Ituff Token', 'ConfigFile', 'ConfigSet','Pin']
    worksheet.write_row(0, 0, header)
    count = 0

    for sicclimit in siccLimits:
        count = count + 1
        row = [sicclimit["TestName"], sicclimit["Mean"], sicclimit["Median"], sicclimit["StdDev"],
               sicclimit["PseduSigma_Upper"], sicclimit["PseduSigma_Lower"], sicclimit["HighLimit"],
               sicclimit["LowLimit"], '']
        worksheet.write_row(count, 0, row)
        worksheet.write_url(count, 9, sicclimit["GraphPath"])

        if sicclimit["TestName"] in existing_limits:
            limits = existing_limits[sicclimit["TestName"]]
            hl = float(limits['HighLimit'])
            ll = float(limits['LowLimit'])
            gsds = limits['GSDS']
            ituff_token = limits['ItuffToken']

            row = [ll, hl, gsds, ituff_token,limits['ConfigFile'], limits['ConfigSet'],limits['Pin']]

            worksheet.write_row(count, 10, row)

    workbook.close()

    return OutFinalCSVPath


def GetBasicParams(datafromCsvDIct, outputPath):
    siccLimits = []

    results_dir = os.path.join(outputPath + '/GraphDataSICCLimits')
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
        print(results_dir + "...Result directory")

    for sicctest in datafromCsvDIct:
        mean, median, std = GetMean(datafromCsvDIct[sicctest][0])
        fileName = results_dir + "//" + sicctest.split("::")[1] + ".png"
        quantile_5 = GetQuantiles(datafromCsvDIct[sicctest][0], 5)
        quantile_95 = GetQuantiles(datafromCsvDIct[sicctest][0], 95)

        psedoSigmaLower = (6 * (median - quantile_5)) / 1.6449
        psedoSigmaUpper = (6 * (quantile_95 - median)) / 1.6449

        highLimit = median + psedoSigmaUpper
        lowLimit = median - psedoSigmaLower

        # GetPercentileForGraph(datafromCsvDIct[sicctest][0], fileName)

        result = {
            "TestName": sicctest,
            "Mean": mean,
            "Median": median,
            "StdDev": std,
            "PseduSigma_Upper": psedoSigmaUpper,
            "PseduSigma_Lower": psedoSigmaLower,
            "HighLimit": highLimit,
            "LowLimit": lowLimit,
            "GraphPath": fileName
        }
        siccLimits.append(result)

    return siccLimits


def GetMean(x):
    mean = np.mean(x)
    median = np.median(x)
    std = np.std(x)

    return mean, median, std


def GetQuantiles(x, percentage):
    pointer = percentage / 100
    quantile = np.quantile(x, pointer)

    return quantile


def GetPercentileForGraph(x, filename):
    maxi = max(x)
    mini = min(x)
    n_bins = len(np.unique(x))
    # n_bins = 100
    sigma = (maxi - mini) / n_bins
    mu = 100

    fig, ax = plt.subplots(figsize=(8, 4))

    # plot the cumulative histogram
    n, bins, patches = ax.hist(x, n_bins, density=True, histtype='step',
                               cumulative=True, label='Empirical')

    # Overlay a reversed cumulative histogram.

    # tidy up the figure
    ax.grid(True)
    ax.legend(loc='right')
    ax.set_title('Cumulative steps')
    ax.set_ylabel('SICC measurement')
    ax.set_xlabel('Percentile')
    plt.savefig(filename, bbox_inches='tight')
    plt.clf()
    plt.close()
