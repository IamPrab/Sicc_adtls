import os
import xml.etree.ElementTree as ET
import os
import pandas as pd
import EditXML_Utils


def ParseApprovalFile(approvalFile):
    excel_data = pd.read_excel(approvalFile)
    dict_data = {}
    data = pd.DataFrame(excel_data, columns=['SICC Test', 'Mean', 'Median', 'Standard Deviation', 'PseduSigma_Upper', 'PseduSigma_Lower',
                                             'HighLimit', 'LowLimit', 'Approval',
                                             'Previous Low Limit', 'Previous High Limit', 'GSDS', 'Ituff Token', 'ConfigFile', 'ConfigSet','Pin'])
    length = (len(data['SICC Test']))
    count = 0
    # print(length)
    while (count < length):
        approval = data['Approval'][count]
        if approval == 'Yes' or approval == 'Y' or approval == 'YES':
            if data['SICC Test'][count] not in dict_data:
                stuff = {
                    'Mean': float(data['Mean'][count]),
                    'Median': float(data['Median'][count]),
                    'StD': float(data['Standard Deviation'][count]),
                    'PseduSigma_Upper': float(data['PseduSigma_Upper'][count]),
                    'PseduSigma_Lower': data['PseduSigma_Lower'][count],
                    'HighLimit': float(data['HighLimit'][count]),
                    'LowLimit': float(data['LowLimit'][count]),
                    'Approval': (data['Approval'][count]),
                    'Previous Low Limit': float(data['Previous Low Limit'][count]),
                    'GSDS': data['GSDS'][count],
                    'Ituff Token': data['Ituff Token'][count],
                    'ConfigFile': data['ConfigFile'][count],
                    'ConfigSet': data['ConfigSet'][count],
                    'Pin': data['Pin'][count]
                }
                dict_data[data['SICC Test'][count]] = stuff
            else:
                print(data['TestName'][count])
                print(dict_data[data['SICC Test'][count]])
                print("double Equation ^^")
            count = count + 1

    return dict_data



def Parse_XML_and_Edit(configFile, config_approval, outputFolder):# configset, lowlimit, highlimit, gsds, itufftoken,outputPath):


    config_debug = outputFolder + "/" + configFile.split('/')[4]
    # parse the XML file
    tree = ET.parse(configFile)

    # get the root element
    root = tree.getroot()

    # iterate over the ConfigList elements
    for config_list in root.findall('./ConfigList'):

        for approval in config_approval:

            highlimit = approval['HighLimit']
            lowlimit = approval['LowLimit']
            itufftoken = approval['Ituff Token']
            gsds = approval['GSDS']
            configset = approval['ConfigSet']
            pin_datalookup = approval['Pin']

            # get the name attribute of the ConfigList element
            config_list_name = config_list.get('name')


            # iterate over the Config elements
            for config in config_list.findall('./Config'):

                # get the Cores element
                cores = config.find('./Cores')
                measurements = config.find('./Measurements')

                # iterate over the Core elements
                for core in cores.findall('./Core'):

                    # get the Equation element
                    equation = core.find('./Equation').text

                    # get the iTuff and GSDS elements
                    ituff = core.find('./iTuff')
                    gsds = core.find('./GSDS')

                    # get the Token element from the iTuff and GSDS elements
                    ituff_token = ituff.find('./Token').text if ituff is not None else None
                    gsds_token = gsds.find('./Token').text if gsds is not None else None
                    # print(ituff_token)
                    # get the LimitLoUserVar and LimitHiUserVar elements
                    if ituff_token == itufftoken:
                        limit_lo = core.find('./LimitLoUserVar').text = str(lowlimit)
                        limit_hi = core.find('./LimitHiUserVar').text = str(highlimit)

                for measurement in measurements.findall('./Measurement'):
                    pin = measurement.find('./Pin').text
                    print(pin)
                    measurement_setting = measurement.find('./MeasurementSettings')

                    if (pin == pin_datalookup):
                        highLim = measurement_setting.find('./limit_high').text = str(lowlimit)
                        lowlim = measurement_setting.find(('./limit_low')).text = str(highlimit)

                    # print(highLim)
                    # print(lowlim)

        tree.write(config_debug)
        print('Debug config written')

def Group_Configs(approvals):

    config_group = {}
    for approval in approvals:
        config = approvals[approval]['ConfigFile']
        if config not in config_group:
            config_group[config] = [approvals[approval]]
        else:
            config_group[config].append(approvals[approval])

    return config_group


def Edit_XML(approvals,tp_path,outputPath):

    outputFolder = outputPath + '/InputFileDebug'
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    config_approvals = Group_Configs(approvals)
    for config_approval in config_approvals:
        config_file = tp_path + config_approval[1:]
        Parse_XML_and_Edit(config_file, config_approvals[config_approval], outputFolder)

    return config_approvals

# print the results
# print(f"ConfigList: {config_list_name}")
# print(f"Equation: {equation}")
# #print(f"LimitLo: {limit_lo}")
# print(f"LimitHi: {limit_hi}")
# print(f"iTuff Token: {ituff_token}")
# print(f"GSDS Token: {gsds_token}")