import os
import unittest

import Utils


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_readcsvSICC_andPerformStuff(self):
        path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\WLB_8PWJ_WLB\\8PWJ_G3074C\\SIU_Test\\JsonVminData"
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

        res = Utils.GetPercentileForGraph(datafromCsvDIct['TPI_SIU_STATIC::SICC_X_AMEAS_K_STRESS_X_X_X_X_FULLCHIP_1P3_VCCANA_EHV_0_LC_2P0'][0])

        self.assertIsNone(res)

    def test_Limits(self):
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

        res = Utils.GetBasicParams(datafromCsvDIct)

        self.assertIsNone(res)


if __name__ == '__main__':
    unittest.main()
