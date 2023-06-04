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
overallKill_limits_prevouseqns = {}


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
    worksheet = workbook.add_worksheet("Config")
    #worksheet2 = workbook.add_worksheet("Proposal")
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
    worksheet = workbook.add_worksheet("Config")
    #worksheet2= workbook.add_worksheet("Proposal")
    header = ['SICC Test', 'Mean', 'Median', 'Standard Deviation','Sigma','PseudoSigma_Upper', 'PseudoSigma_Lower', 'HighLimit- PseuduSigma',
              'LowLimit- PseudoSigma','DPW-PseudoSigma','psedo_DPW_TGood', 'psedo_DPW_TBad', 'HighLimit - StdSigma', 'LowLimit - StdSigma',
              'DPW-StdSigma','std_DPW_TGood', 'std_DPW_TBad',
              'Eng_Limit High','Eng_Limit_Low','OverRide Sigma', 'Approval','Graph','Jmp Graphs Live',
              'Previous High Limit', 'Previous Low Limit','DPW_Previous_Equation','prev_DPW_TGood','prev_DPW_TBad',
              'DPW-PseudoSigma8','psedo_DPW_TGood_Sigma8', 'psedo_DPW_TBad_Sigma8','DPW-StdSigma8','std_DPW_TGood_Sigma8', 'std_DPW_TBad_Sigma8',
              'DPW-PseudoSigma10', 'psedo_DPW_TGood_Sigma10', 'psedo_DPW_TBad_Sigma10', 'DPW-StdSigma10','std_DPW_TGood_Sigma10', 'std_DPW_TBad_Sigma10',
              'GSDS', 'Ituff Token', 'ConfigFile', 'ConfigSet','Pin']
    worksheet.write_row(0, 0, header)
    count = 0
    link_tracker = {}
    #worksheet2.write_row(0,0,["jkh","bhbg"])
    for sicclimit in siccLimits:
        count = count + 1
        row = [sicclimit["TestName"], sicclimit["Mean"], sicclimit["Median"], sicclimit["StdDev"],sicclimit["Sigma"],
               sicclimit["PseduSigma_Upper"], sicclimit["PseduSigma_Lower"], sicclimit["HighLimit"],sicclimit["LowLimit"],
               sicclimit['psedu_DPW'], sicclimit['psedo_DPW_TGood'], sicclimit['psedo_DPW_TBad'],
               sicclimit['SigmaUpper'], sicclimit['SigmaLower'], sicclimit['std_DPW'], sicclimit['std_DPW_TGood'], sicclimit['std_DPW_TBad'],
               '','','','']
        worksheet.write_row(count, 0, row)
        worksheet.write_url(count, 21, sicclimit["GraphPath"], string = 'Open Graph')

        if Data_Link[sicclimit["TestName"]] not in link_tracker:
            url = WriteJslFile(outputPath, Data_Link[sicclimit["TestName"]])
            link_tracker[Data_Link[sicclimit["TestName"]]] = True
            worksheet.write_url(count, 22, url)

        if sicclimit["TestName"] in existing_limits:
            limits = existing_limits[sicclimit["TestName"]]
            hl = float(limits['HighLimit'])
            ll = float(limits['LowLimit'])
            gsds = limits['GSDS']
            ituff_token = limits['ItuffToken']

            row = [hl, ll,sicclimit['prev_DPW'],sicclimit['prev_DPW_TGood'], sicclimit['prev_DPW_TBad'],
                   sicclimit['psedu_DPW_8Sigma'],sicclimit['psedo_DPW_TGood_8Sigma'],sicclimit['psedo_DPW_TBad_8Sigma'],
                   sicclimit['std_DPW_8Sigma'],sicclimit['std_DPW_TGood_8Sigma'],sicclimit['std_DPW_TBad_8Sigma'],
                   sicclimit['psedu_DPW_10Sigma'], sicclimit['psedo_DPW_TGood_10Sigma'],sicclimit['psedo_DPW_TBad_10Sigma'],
                   sicclimit['std_DPW_10Sigma'], sicclimit['std_DPW_TGood_10Sigma'], sicclimit['std_DPW_TBad_10Sigma'],
                    gsds, ituff_token,limits['ConfigFile'], limits['ConfigSet'],limits['Pin']]

            worksheet.write_row(count, 23, row)
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

def GetDPWForLimits(data, highLimit_psedo ,lowLimit_psedo, highLimit_std, lowLimit_std, prevHighLim, prevLowLim, uniqueId, test):

    kills_psedu = []
    kills_goodDiePsedu = 0
    kills_BadDiePsedu = 0
    kills_std = []
    kills_goodDieSTD = 0
    kills_BadDieSTD = 0
    kills_prev = []
    kills_goodDiePrev = 0
    kills_BadDiePrev = 0
    quant = len(data)-1
    for i in range(quant):
        point = float(data[i])
        id = uniqueId[i]
        bin = id.split('%')[4]
        #print(id)
        if point > float(highLimit_psedo) or point < float(lowLimit_psedo):
            kills_psedu.append(point)
            if float(bin) == 1 or float(bin) == 2:
                kills_goodDiePsedu += 1
            else:
                kills_BadDiePsedu += 1
            #print(point, highLimit_psedo)
            if id not in overallKill_limits_psedosigma:
                overallKill_limits_psedosigma[id]= [test]
            else:
                if overallKill_limits_psedosigma[id] != None:
                    overallKill_limits_psedosigma[id] = overallKill_limits_psedosigma[id].append(test)


        if point > float(highLimit_std) or point < float(lowLimit_std):
            kills_std.append(point)
            if float(bin) == 1 or float(bin) == 2:
                kills_goodDieSTD += 1
            else:
                kills_BadDieSTD += 1
            if id not in overallKill_limits_stdLimits:
                overallKill_limits_stdLimits[id]= []
                overallKill_limits_stdLimits[id].append(test)
            else:
                if overallKill_limits_stdLimits[id] != None:
                    overallKill_limits_stdLimits[id]= overallKill_limits_stdLimits[id].append(test)

        if point > float(prevHighLim) or point < float(prevLowLim):
            kills_prev.append(point)
            if float(bin) == 1 or float(bin) == 2:
                kills_goodDiePrev += 1
            else:
                kills_BadDiePrev += 1
            if id not in overallKill_limits_prevouseqns:
                overallKill_limits_prevouseqns[id] = []
                overallKill_limits_prevouseqns[id].append(test)
            else:
                if overallKill_limits_prevouseqns[id] != None:
                    overallKill_limits_prevouseqns[id] = overallKill_limits_prevouseqns[id].append(test)

    #print(len(overallKill_limits_stdLimits), len(overallKill_limits_psedosigma))
    binsKills = [kills_goodDiePsedu, kills_BadDiePsedu, kills_goodDieSTD, kills_BadDieSTD, kills_goodDiePrev, kills_BadDiePrev]

    return kills_psedu, kills_std, kills_prev, binsKills


def GetBasicParams(datafromCsvDIct, outputPath, existing_limits):
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
        psedoSigmaLower8Sigma = (8 * (median - quantile_5)) / 1.6449
        psedoSigmaUpper8Sigma = (8 * (quantile_95 - median)) / 1.6449
        psedoSigmaLower10Sigma = (10 * (median - quantile_5)) / 1.6449
        psedoSigmaUpper10Sigma = (10 * (quantile_95 - median)) / 1.6449

        highLimit_psedo = median + psedoSigmaUpper
        lowLimit_psedo = median - psedoSigmaLower
        highLimit_psedo8Sigma = median + psedoSigmaUpper8Sigma
        lowLimit_psedo8Sigma = median - psedoSigmaLower8Sigma
        highLimit_psedo10Sigma = median + psedoSigmaUpper10Sigma
        lowLimit_psedo10Sigma = median - psedoSigmaLower10Sigma

        sigmaUpper_std = (6 * std) + median
        sigmaLower_std = median - (6 * std)
        sigmaUpper_std8Sigma = (8 * std) + median
        sigmaLower_std8Sigma = median - (8 * std)
        sigmaUpper_std10Sigma = (10 * std) + median
        sigmaLower_std10Sigma = median - (10 * std)

        LimitsSigmas = {
            'psedoSigmaLower' : lowLimit_psedo,
            'psedoSigmaUpper' : highLimit_psedo,
            'psedoSigmaLower8Sigma' : highLimit_psedo8Sigma,
            'psedoSigmaUpper8Sigma' : lowLimit_psedo8Sigma,
            'psedoSigmaLower10Sigma' : highLimit_psedo10Sigma,
            'psedoSigmaUpper10Sigma' : lowLimit_psedo10Sigma,
            'sigmaUpper_std' : sigmaUpper_std,
            'sigmaLower_std' : sigmaLower_std,
            'sigmaUpper_std8Sigma' : sigmaUpper_std8Sigma,
            'sigmaLower_std8Sigma' : sigmaLower_std8Sigma,
            'sigmaUpper_std10Sigma' : sigmaUpper_std10Sigma,
            'sigmaLower_std10Sigma' : sigmaLower_std10Sigma
        }

        GetPercentileForGraph(datafromCsvDIct[sicctest][0], fileName, median, LimitsSigmas)


        old_HighLimit = 0
        old_LowLimit = 0

        if sicctest in existing_limits:
            old_HighLimit = existing_limits[sicctest]["HighLimit"]
            old_LowLimit = existing_limits[sicctest]["LowLimit"]

        psedu_DPW, std_DPW, prevDPW,binsKills = GetDPWForLimits(datafromCsvDIct[sicctest][0], highLimit_psedo, lowLimit_psedo,
                                                                sigmaUpper_std, sigmaLower_std, old_HighLimit,old_LowLimit,datafromCsvDIct[sicctest][1], sicctest)
        psedu_DPW8Sigma, std_DPW8Sigma, prevDPW8Sigma, binsKills8Sigma = GetDPWForLimits(datafromCsvDIct[sicctest][0], highLimit_psedo8Sigma,
                                                                 lowLimit_psedo8Sigma,
                                                                 sigmaUpper_std8Sigma, sigmaLower_std8Sigma, old_HighLimit,
                                                                 old_LowLimit, datafromCsvDIct[sicctest][1], sicctest)
        psedu_DPW10Sigma, std_DPW10Sigma, prevDPW10Sigma, binsKills10Sigma = GetDPWForLimits(datafromCsvDIct[sicctest][0], highLimit_psedo10Sigma,
                                                                 lowLimit_psedo10Sigma,
                                                                 sigmaUpper_std10Sigma, sigmaLower_std10Sigma, old_HighLimit,
                                                                 old_LowLimit, datafromCsvDIct[sicctest][1], sicctest)

        psedu_DPW_len = len(psedu_DPW)
        std_DPW_len = len(std_DPW)
        prev_DPW_len = len(prevDPW)
        psedu_DPW_len8Sigma = len(psedu_DPW8Sigma)
        std_DPW_len8Sigma = len(std_DPW8Sigma)
        psedu_DPW_len10Sigma = len(psedu_DPW)
        std_DPW_len10Sigma = len(std_DPW)

        wafersListCount = outputPath + '/WaferCount.txt'
        if os.path.isfile(wafersListCount):
            f = open(wafersListCount)
            num_lines = int(f.read())
            psedu_DPW_len = psedu_DPW_len / num_lines
            std_DPW_len = std_DPW_len / num_lines
            prev_DPW_len = prev_DPW_len / num_lines
            psedu_DPW_len8Sigma = psedu_DPW_len8Sigma / num_lines
            std_DPW_len8Sigma = std_DPW_len8Sigma /num_lines
            psedu_DPW_len10Sigma = psedu_DPW_len10Sigma /num_lines
            std_DPW_len10Sigma = std_DPW_len10Sigma / num_lines

            for binkills in binsKills:
                binkills = binkills/num_lines

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
            "std_DPW" : std_DPW_len,
            "prev_DPW" : prev_DPW_len,
            "psedo_DPW_TGood" : binsKills[0],
            "psedo_DPW_TBad" : binsKills[1],
            "std_DPW_TGood" : binsKills[2],
            "std_DPW_TBad" : binsKills[3],
            "prev_DPW_TGood" : binsKills[4],
            "prev_DPW_TBad": binsKills[5],
            "psedu_DPW_8Sigma": psedu_DPW_len8Sigma,
            "std_DPW_8Sigma" : std_DPW_len8Sigma,
            "psedo_DPW_TGood_8Sigma" : binsKills8Sigma[0],
            "psedo_DPW_TBad_8Sigma" : binsKills8Sigma[1],
            "std_DPW_TGood_8Sigma" : binsKills8Sigma[2],
            "std_DPW_TBad_8Sigma" : binsKills8Sigma[3],
            "psedu_DPW_10Sigma": psedu_DPW_len10Sigma,
            "std_DPW_10Sigma" : std_DPW_len10Sigma,
            "psedo_DPW_TGood_10Sigma" : binsKills10Sigma[0],
            "psedo_DPW_TBad_10Sigma" : binsKills10Sigma[1],
            "std_DPW_TGood_10Sigma" : binsKills10Sigma[2],
            "std_DPW_TBad_10Sigma" : binsKills10Sigma[3]
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


def GetPercentileForGraph(x, filename,  median, LimitSigmas):
    maxi = max(x)
    mini = min(x)
    n_bins = len(np.unique(x))
    # n_bins = 100
    sigma = (maxi - mini) / n_bins
    mu = 100

    percentiles = np.percentile(x, np.arange(0, 100, 0.5))

    # Plotting
    plt.figure(figsize=(7, 7))
    plt.plot(percentiles, np.arange(0, 100, 0.5), 'o', markersize=3, label = 'Values')
    plt.xlabel('Percentile')
    plt.ylabel('Values')
    plt.title('Percentile Plot')
    plt.grid(True)
    plt.axvline(x=float(median),color = 'black', label = 'Median')
    plt.axvline(x=float(LimitSigmas['psedoSigmaLower']), color = 'red', label = 'PsedoSigmaLimit Sigma 6')
    plt.axvline(x=float(LimitSigmas['psedoSigmaUpper']), color='red')
    plt.axvline(x=float(LimitSigmas['psedoSigmaLower8Sigma']), color='grey', linestyle = '--',label = 'PsedoSigmaLimit Sigma 8')
    plt.axvline(x=float(LimitSigmas['psedoSigmaUpper8Sigma']), color='grey',linestyle = '--', )
    light_blue = (0.7, 0.7, 1.0)
    plt.axvline(x=float(LimitSigmas['psedoSigmaLower10Sigma']), color=light_blue,linestyle = '--', label = 'PsedoSigmaLimit Sigma 10')
    plt.axvline(x=float(LimitSigmas['psedoSigmaUpper10Sigma']), color=light_blue,linestyle = '--')
    plt.axvline(x=float(LimitSigmas['sigmaLower_std']), color='green', label='STD_Limits')
    plt.axvline(x=float(LimitSigmas['sigmaUpper_std']), color='green')
    light_green = (0.678, 0.847, 0.655)
    plt.axvline(x=float(LimitSigmas['sigmaUpper_std8Sigma']), color=light_green,linestyle = '--', label='STD_Limits Sigma 8')
    plt.axvline(x=float(LimitSigmas['sigmaLower_std8Sigma']), color=light_green,linestyle = '--')
    light_pink = (1.0, 0.714, 0.757)
    plt.axvline(x=float(LimitSigmas['sigmaUpper_std10Sigma']), color=light_pink,linestyle = '--', label='STD_Limits Sigma 10')
    plt.axvline(x=float(LimitSigmas['sigmaLower_std10Sigma']), color=light_pink,linestyle = '--')
    plt.legend( bbox_to_anchor=(1.05, 1), loc='upper left')
    # Adjust figure boundaries if necessary
    plt.tight_layout()


    # legval = ["blue", "orange"]
    # legend_ax = plt.gca().twinx()  # Create a twin Axes object
    # legend_ax.set_axis_off()  # Turn off the axis for the twin Axes
    # legend_ax.legend(
    #     [plt.Line2D([0], [0], marker='o', color='w', label=legval[i], markerfacecolor=legval[i], markersize=8) for i in
    #      range(len(legval))],
    #     legval, loc='upper left', bbox_to_anchor=(1.05, 1))

    # Adjust figure boundaries if necessary
    plt.tight_layout()


    plt.savefig(filename, bbox_inches='tight')
    #plt.show()
    plt.clf()
    plt.close()

def GetPercentileForGraph2(x, filename, psedoSigmaLower, psedoSigmaUpper, highLimit, lowLimit, median):
    maxi = max(x)
    mini = min(x)
    n_bins = len(np.unique(x))
    # n_bins = 100
    sigma = (maxi - mini) / n_bins
    mu = 100

    percentiles = np.percentile(x, np.arange(0, 100, 0.5))

    # Plotting
    plt.figure(figsize=(6,8))
    plt.plot(percentiles, np.arange(0, 100, 0.5), 'o', markersize=3)
    plt.xlabel('Percentile')
    plt.ylabel('Values')
    plt.title('Percentile Plot')
    plt.grid(True)
    plt.show()
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
