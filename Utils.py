import gc
import math
import multiprocessing
import os
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import combinations

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

Data_Link = {}

overallKill_limits_psedosigma = {}
overallKill_limits_stdLimits = {}


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
                Data_Link[testname] = datafile
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
    uniqueId = []
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
                uniqueId_val = data_instance_x[1][data_instance_x[1].index(val)]

                x.append(x_val)
                y.append(y_val)
                uniqueId.append(uniqueId_val)

    return x, y, uniqueId

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

                        x1, x2, uniqueId = get_x_y_pair(x1, x2)

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
    pairsofTests = {}

    for testname in dictData:
        for pair in Pairs:
            if testname.find(pair) > 0:
                pairTest = testname.replace(pair, Pairs[pair])

                pairToGo = [testname, pairTest]
                key = testname + '@'+ pairTest
                pairsofTests[key] = 0.9

    return pairsofTests

def GetDPW(m, b, x, y, uniqueID):
    passBucketY = 0
    killBucketY = {}
    uniquekillsBucket = []

    kb1,kb2,kb3,kb4,kb5,kb43 = ({} for i in range (6))

    count = 0
    while (count < len(y)):
        kill_line =  b + (m * x[count])
        bin = uniqueID[count].split("%")[4]
        uniqueID[count] = uniqueID[count]
        if y[count] >= kill_line:
            if uniqueID[count] not in killBucketY:
                killBucketY[uniqueID[count]] = uniqueID[count]

            if bin == "1":
                if uniqueID[count] not in kb1:
                    kb1[uniqueID[count]]= uniqueID[count]
            elif bin == "2":
                if uniqueID[count] not in kb2:
                    kb2[uniqueID[count]]= uniqueID[count]
            elif bin == "3":
                if uniqueID[count] not in kb3:
                    kb3[uniqueID[count]]= uniqueID[count]
            elif bin == "5":
                if uniqueID[count] not in kb5:
                    kb5[uniqueID[count]]= uniqueID[count]
            elif bin == "4":
                if uniqueID[count] not in kb4:
                    kb4[uniqueID[count]]= uniqueID[count]
            elif bin == "43":
                if uniqueID[count] not in kb43:
                    kb43[uniqueID[count]]= uniqueID[count]
        else:
            passBucketY = passBucketY + 1
        count = count + 1
        #print(killBucketY)

    passToKillBucket = [len(killBucketY), len(kb1), len(kb2), len(kb3), len(kb4), len(kb5), len(kb43)]
    #print(passToKillBucket)


    return passToKillBucket

def getLinePoints(x, y, b, m):
    c = 0
    linePoints = []
    while (c < len(x)):
        z = m * x[c] + b
        linePoints.append(z)
        c = c + 1
    return linePoints

def GetFitLines(x, y, unique_id):
    intercept, slope = polyfit(x, y, 1)
    linePoints = getLinePoints(x, y, intercept, slope)
    MSE = np.square(np.subtract(y, linePoints)).mean()
    RMSE = math.sqrt(MSE)
    intercept_kill = float(intercept) + (6*float(RMSE))
    DPW = GetDPW(slope, intercept_kill, x, y, unique_id)

    result_dict = {
        'Slope': slope,
        'Intercept_kill': intercept_kill,
        'Intercept': intercept,
        'RMSE': RMSE,
        'DPW': DPW
    }

    return result_dict


def CalFits(pairs, datafromCsvDIct):
    pairFits = {}
    for pair in pairs:
        x_y = pair.split('@')
        x, y, unique_id = get_x_y_pair(datafromCsvDIct[x_y[0]], datafromCsvDIct[x_y[1]])
        fit = GetFitLines(x, y, unique_id)

        pairFits[pair] = fit

    return pairFits



def WriteTOApprovalFile(pairFits, path):
    OutFinalCSVPath = path + "\\SICCApproval.xlsx"
    workbook = xlsxwriter.Workbook(OutFinalCSVPath)
    worksheet = workbook.add_worksheet()
    header = ['SICC Test X', 'SICC Test Y', 'Slope', 'Intercept', 'RMSE', 'DPW']
    worksheet.write_row(0, 0, header)
    count = 0
    datafileTracker = {}

    for pairFit in pairFits:
        count = count + 1
        names = pairFit.split('@')
        data = pairFits[pairFit]

        wafersListCount = path + '/WaferCount.txt'
        dpwPerBin = []
        if os.path.isfile(wafersListCount):
            f = open(wafersListCount)
            num_lines = int(f.read())
            for killperbin in data['DPW']:
                dpwPerBin.append(killperbin / num_lines)

        #print(dpwPerBin)
        row = [names[0], names[1], data['Slope'], data['Intercept'], data['RMSE'], dpwPerBin[0]]
        worksheet.write_row(count, 0, row)

        graphName = path + "\\GraphDataSICC\\" + pairFit.split('::')[0] + '_' + str(count) + '.png'
        worksheet.write_url(count, 6, graphName, string = 'Open Graph')

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

    x, y, unique_id = get_x_y_pair(X_Data, Y_Data)
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
    else:
        if '::' in Y_name:
            filename = results_dir + "\\" + X_name + '@' + Y_name.split('::')[0] + '_' + str(count + 1) + ".png"

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

def WriteJslFile(outputPath, DataLink):

    results_dir = os.path.join(outputPath + '/JmpGraphsScripts')
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
        print(results_dir + "...Result directory")

    name = DataLink.split('.csv')[0].split('DataFile')[1]
    name = results_dir + "/JmpScriptRunner" + name + ".jsl"
    file = open(name, "w")
    approvalFile = outputPath + "\SICCApprovalLimits.xlsx"
    jslScript = "\\\pjwade-desk.ger.corp.intel.com\AXEL_ADTL_REPORTS\AXEL_SICC_LIMITS_REPORT\plotAxelLimitsFunction.jsl"
    # Write the code to the file
    file.write(f"//!\nInclude(\"{jslScript}\" );"
               f"\n\nplotLimits(\"{DataLink}\", \"{approvalFile}\");")
    # Close the file
    file.close()

    return name

def WriteToFile(siccLimits, outputPath, existing_limits):
    OutFinalCSVPath = outputPath + "\\SICCApprovalLimits.xlsx"
    workbook = xlsxwriter.Workbook(OutFinalCSVPath)
    worksheet = workbook.add_worksheet()
    header = ['SICC Test', 'Mean', 'Median', 'Standard Deviation','Sigma','PseudoSigma_Upper', 'PseudoSigma_Lower', 'HighLimit- PseuduSigma',
              'LowLimit- PseudoSigma','DPW-PseudoSigma', 'HighLimit - StdSigma', 'LowLimit - StdSigma','DPW-StdSigma',
              'Eng_Limit High','Eng_Limit_Low','OverRide Sigma', 'Approval','Graph','Jmp Graphs Live',
              'Previous High Limit', 'Previous Low Limit', 'GSDS', 'Ituff Token', 'ConfigFile', 'ConfigSet','Pin']
    worksheet.write_row(0, 0, header)
    count = 0
    link_tracker = {}
    for sicclimit in siccLimits:
        count = count + 1
        row = [sicclimit["TestName"], sicclimit["Mean"], sicclimit["Median"], sicclimit["StdDev"],sicclimit["Sigma"],
               sicclimit["PseduSigma_Upper"], sicclimit["PseduSigma_Lower"], sicclimit["HighLimit"],sicclimit["LowLimit"],sicclimit['psedu_DPW'],
               sicclimit['SigmaUpper'], sicclimit['SigmaLower'], sicclimit['std_DPW'],'','','','']
        worksheet.write_row(count, 0, row)
        worksheet.write_url(count, 17, sicclimit["GraphPath"], string = 'Open Graph')

        if Data_Link[sicclimit["TestName"]] not in link_tracker:
            url = WriteJslFile(outputPath, Data_Link[sicclimit["TestName"]])
            link_tracker[Data_Link[sicclimit["TestName"]]] = True
            worksheet.write_url(count, 18, url)

        if sicclimit["TestName"] in existing_limits:
            limits = existing_limits[sicclimit["TestName"]]
            hl = float(limits['HighLimit'])
            ll = float(limits['LowLimit'])
            gsds = limits['GSDS']
            ituff_token = limits['ItuffToken']

            row = [hl, ll, gsds, ituff_token,limits['ConfigFile'], limits['ConfigSet'],limits['Pin']]

            worksheet.write_row(count, 19, row)
    with open(outputPath+'/KillsPseudo.txt', 'w') as data:
        data.write(str(overallKill_limits_psedosigma))
    with open(outputPath + '/KillsStd.txt', 'w') as data:
        data.write(str(overallKill_limits_stdLimits))
    wafersListCount = outputPath + '/WaferCount.txt'
    num_lines = 1
    if os.path.isfile(wafersListCount):
        f = open(wafersListCount)
        num_lines = int(f.read())
    Overall_Dpw = ['DPWOverAll_PseudoSigma:', len(overallKill_limits_psedosigma)/num_lines,'DPWOverAll_StdSigma:', len(overallKill_limits_stdLimits)/num_lines]
    worksheet.write_row(count+1, 0, Overall_Dpw)

    workbook.close()

    return OutFinalCSVPath

def GetDPWForLimits(data, highLimit_psedo ,lowLimit_psedo, highLimit_std, lowLimit_std, uniqueId, test):

    kills_psedu = []
    kills_std = []
    quant = len(data)-1
    for i in range(quant):
        point = float(data[i])
        id = uniqueId[i]
        if point > float(highLimit_psedo) or point < float(lowLimit_psedo):
            kills_psedu.append(point)
            #print(point, highLimit_psedo)
            if id not in overallKill_limits_psedosigma:
                overallKill_limits_psedosigma[id]= [test]
            else:
                if overallKill_limits_psedosigma[id] != None:
                    overallKill_limits_psedosigma[id] = overallKill_limits_psedosigma[id].append(test)
        if point > float(highLimit_std) or point < float(lowLimit_std):
            kills_std.append(point)
            if id not in overallKill_limits_stdLimits:
                overallKill_limits_stdLimits[id]= []
                overallKill_limits_stdLimits[id].append(test)
            else:
                if overallKill_limits_stdLimits[id] != None:
                    overallKill_limits_stdLimits[id]= overallKill_limits_stdLimits[id].append(test)
    #print(len(overallKill_limits_stdLimits), len(overallKill_limits_psedosigma))

    return kills_psedu,kills_std


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

        psedoSigmaValLower = (1 * (median - quantile_5)) / 1.6449
        psedoSigmaValUpper = (1 * (quantile_95 - median)) / 1.6449

        psedoSigmaLower = (6 * (median - quantile_5)) / 1.6449
        psedoSigmaUpper = (6 * (quantile_95 - median)) / 1.6449

        highLimit_psedo = median + psedoSigmaUpper
        lowLimit_psedo = median - psedoSigmaLower

        sigmaUpper_std = (6 * std) + median
        sigmaLower_std = median - (6 * std)

        GetPercentileForGraph(datafromCsvDIct[sicctest][0], fileName, lowLimit_psedo, highLimit_psedo, sigmaUpper_std, sigmaLower_std, median)

        psedu_DPW, std_DPW = GetDPWForLimits(datafromCsvDIct[sicctest][0], highLimit_psedo, lowLimit_psedo, sigmaUpper_std, sigmaLower_std, datafromCsvDIct[sicctest][1], sicctest)

        psedu_DPW_len = len(psedu_DPW)
        std_DPW_len = len(std_DPW)
        wafersListCount = outputPath + '/WaferCount.txt'
        if os.path.isfile(wafersListCount):
            f = open(wafersListCount)
            num_lines = int(f.read())
            psedu_DPW_len = psedu_DPW_len / num_lines
            std_DPW_len = std_DPW_len / num_lines

        result = {
            "Sigma": float(6),
            "TestName": sicctest,
            "Mean": mean,
            "Median": median,
            "StdDev": std,
            "PseduSigma_Upper": psedoSigmaValUpper,
            "PseduSigma_Lower": psedoSigmaValLower,
            "HighLimit": highLimit_psedo,
            "LowLimit": lowLimit_psedo,
            "GraphPath": fileName,
            "SigmaUpper": sigmaUpper_std,
            "SigmaLower": sigmaLower_std,
            "psedu_DPW": psedu_DPW_len,
            "std_DPW" : std_DPW_len
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


def GetPercentileForGraph(x, filename, psedoSigmaLower, psedoSigmaUpper, highLimit, lowLimit, median):
    maxi = max(x)
    mini = min(x)
    n_bins = len(np.unique(x))
    # n_bins = 100
    sigma = (maxi - mini) / n_bins
    mu = 100

    fig, ax = plt.subplots(figsize=(8, 4))
    plt.axvline(x=median, color ='g',label='Median')
    plt.axvline(x=psedoSigmaLower, color = 'r', label= 'psedoSigma')
    plt.axvline(x=psedoSigmaUpper, color = 'r')
    plt.axvline(x=lowLimit, color = 'm',label= 'std Sigma')
    plt.axvline(x=highLimit, color = 'm')
    plt.axvline(label = f'Max:{maxi}', color = 'aqua')
    plt.axvline(label=f'Min:{mini}', color = 'aqua')

    # plot the cumulative histogram
    n, bins, patches = ax.hist(x, n_bins, density=True, histtype='step',
                               cumulative=True, label='Empirical')

    # Overlay a reversed cumulative histogram.

    # tidy up the figure
    ax.grid(True)
    ax.legend(loc='right')
    ax.set_title('Cumulative steps')
    ax.set_xlabel('SICC measurement')
    ax.set_ylabel('Percentile')
    plt.savefig(filename, bbox_inches='tight')
    legend = plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    plt.clf()
    plt.close()


###################################################################################################################################################################


def GetIdvNameAndData(datafromCsvDIct):
    idvData = {}
    for key in datafromCsvDIct:
        if key.find('::')<1:
            idvData[key] = datafromCsvDIct[key]

    return idvData

def get_idv_sicc_pairs(datafromCsvDIct, idvData):

    idv = 'EMPLY'
    pair_sicc_idv = {}

    for key in idvData :
        idv = key

    for test in datafromCsvDIct:
        if test != idv:
            key = idv + '@' + test
            pair_sicc_idv[key] = 0.99
    return pair_sicc_idv
