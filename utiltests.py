import os
import unittest

from xml.etree import ElementTree as ET
from xml.dom import minidom

from lxml import etree

import EditXML_Utils
import Utils


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_readcsvSICC_andPerformStuff(self):
        path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\WLB_8PWJ_WLB\\8PWJ_G3074C\\SIU_Test\\csvSiccData"
        outputPath = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\WLB_8PWJ_WLB\\8PWJ_G3074C\\SIU_Test"

        subfolders_site = [f.path for f in os.scandir(path) if f.is_dir()]

        datafromCsvDIct = {}

        for site in subfolders_site:
            datafiles = os.listdir(site)
            for i in range(len(datafiles)):
                datafiles[i] = os.path.join(site, datafiles[i])

            datafromCsvDIct = Utils.readcsvSICC(datafiles)

        pairs = Utils.CorrelationValues(datafromCsvDIct)

        # pairs = Utils.createPairs(datafromCsvDIct)

        pairFits = Utils.CalFits(pairs, datafromCsvDIct)

        OutPutApproval = Utils.WriteTOApprovalFile(pairFits, outputPath)

        self.assertIsNone(OutPutApproval)

    def test_CorrelationVlaues(self):
        path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\WLB_8PWJ_WLB\\8PWJ_G3074C\\SIU_Test\\csvSiccData"

        subfolders_site = [f.path for f in os.scandir(path) if f.is_dir()]

        datafromCsvDIct = {}

        for site in subfolders_site:
            datafiles = os.listdir(site)
            for i in range(len(datafiles)):
                datafiles[i] = os.path.join(site, datafiles[i])

            datafromCsvDIct = Utils.readcsvSICC(datafiles)

        corr = Utils.CorrelationValues(datafromCsvDIct)
        self.assertIsNone(corr)

    def test_get_x_y_pair(self):
        path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\WLB_8PWJ_WLB\\8PWJ_G3074C\\SIU_Test\\csvSiccData"

        subfolders_site = [f.path for f in os.scandir(path) if f.is_dir()]

        datafromCsvDIct = {}

        for site in subfolders_site:
            datafiles = os.listdir(site)
            for i in range(len(datafiles)):
                datafiles[i] = os.path.join(site, datafiles[i])

            datafromCsvDIct = Utils.readcsvSICC(datafiles)

        a,b = Utils.get_x_y_pair(datafromCsvDIct['TPI_SIU_STATIC::SICC_X_AMEAS_K_STRESS_X_X_X_X_FULLCHIP_1P3_VCCANA_EHV_0_LC_2P0'],datafromCsvDIct['TPI_SIU_STATIC::SICC_X_AMEAS_K_STRESS_X_X_X_X_FULLCHIP_1P3_VCCANA_EHV_1_LC_2P0'])

        self.assertIsNone(a)


    def test_Graphs(self):
        approvalFile = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\WLB_8PWJ_WLB\\8PWJ_G3074C\\SIU_Test\\SICCApproval.xlsx"
        approvalFileData = Utils.ReadApprovalFile(approvalFile)

        path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\WLB_8PWJ_WLB\\8PWJ_G3074C\\SIU_Test\\csvSiccData"
        outputPath = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\WLB_8PWJ_WLB\\8PWJ_G3074C\\SIU_Test"

        subfolders_site = [f.path for f in os.scandir(path) if f.is_dir()]

        datafromCsvDIct = {}

        for site in subfolders_site:
            datafiles = os.listdir(site)
            for i in range(len(datafiles)):
                datafiles[i] = os.path.join(site, datafiles[i])

            datafromCsvDIct = Utils.readcsvSICC(datafiles)

        res = Utils.GraphFactory(approvalFileData, datafromCsvDIct, outputPath)

        self.assertIsNone(res)

    def test_GraphsForLimits(self):
        approvalFile = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\AXEL_SICC_LIMITS_REPORT\\RPL_8PQF_RPL\\test\\SICCApprovalLimits.xlsx"
        approvalFileData = Utils.ReadApprovalFile(approvalFile)

        path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\AXEL_SICC_LIMITS_REPORT\\RPL_8PQF_RPL\\test\\csvSiccData"
        outputPath = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\AXEL_SICC_LIMITS_REPORT\\RPL_8PQF_RPL\\test"

        subfolders_site = [f.path for f in os.scandir(path) if f.is_dir()]

        datafromCsvDIct = {}

        for site in subfolders_site:
            datafiles = os.listdir(site)
            for i in range(len(datafiles)):
                datafiles[i] = os.path.join(site, datafiles[i])

            datafromCsvDIct = Utils.readcsvSICC(datafiles)

        res = Utils.GetPercentileForGraph2(datafromCsvDIct['TPI_SIU_STATIC::SICC_X_AMEAS_K_STRESS_X_X_X_X_FULLCHIP_1P3_VCCANA_EHV_0_LC_2P0'][0])

        self.assertIsNone(res)

    def test_Limits(self):
        #approvalFile = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\WLB_8PWJ_WLB\\8PWJ_G3074C\\SIU_Test\\SICCApproval.xlsx"
        #approvalFileData = Utils.ReadApprovalFile(approvalFile)

        path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\AXEL_SICC_LIMITS_REPORT\\RPL_8PQF_RPL\\test\\csvSiccData"
        outputPath = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\AXEL_SICC_LIMITS_REPORT\\RPL_8PQF_RPL\\test"

        subfolders_site = [f.path for f in os.scandir(path) if f.is_dir()]

        datafromCsvDIct = {}

        for site in subfolders_site:
            datafiles = os.listdir(site)
            for i in range(len(datafiles)):
                datafiles[i] = os.path.join(site, datafiles[i])

            datafromCsvDIct = Utils.readcsvSICC(datafiles)

        existing_limits = Utils.ReadOldData(outputPath)
        siccLimits = Utils.GetBasicParams(datafromCsvDIct, outputPath)
        print("Limits Calculated")
        res = Utils.WriteToFile(siccLimits, outputPath, existing_limits)

        self.assertIsNone(res)

    def test_ReadOldData(self):
        outputPath = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\WLB_8PWJ_WLB\\8PWJ_G3074C\\SIU_Test"

        res = Utils.ReadOldData(outputPath)
        self.assertIsNone(res)

    def test_EditXML(self):
        tp_path = "C:\\MVs\\RPLSDJXB1H72A032313"
        approval_file = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\AXEL_SICC_LIMITS_REPORT\\RPL_8PQF_RPL\\8PQF_H72A03\\Run2\\SICCApprovalLimits.xlsx"
        outputPath = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\AXEL_SICC_LIMITS_REPORT\\RPL_8PQF_RPL\\8PQF_H72A03\\Run2"

        approvals = EditXML_Utils.ParseApprovalFile(approval_file)

        rs = EditXML_Utils.Edit_XML(approvals, tp_path, outputPath)
        self.assertIsNone(rs)

    def test_prettify(self):

        filexml = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\AXEL_SICC_LIMITS_REPORT\\RPL_8PQF_RPL\\test\InputFileDebug\\RPL_FC.xml"
        tree = etree.parse(filexml)
        root = tree.getroot()

        for elem in root.iter('*'):
            if elem.text is not None:
                elem.text = elem.text.strip()

        xmlstr = etree.tostring(root)
        with open(filexml, 'wb') as f:
            f.write(xmlstr)


if __name__ == '__main__':
    unittest.main()
