import os

import Utils


def test_get_idv_name_and_data():
    path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\EMR_8PRF_EMR\\8PRF_H34F00\\SICC_test\\csvSiccData"

    subfolders_site = [f.path for f in os.scandir(path) if f.is_dir()]

    datafromCsvDIct = {}

    for site in subfolders_site:
        datafiles = os.listdir(site)
        for i in range(len(datafiles)):
            datafiles[i] = os.path.join(site, datafiles[i])

        datafromCsvDIct = Utils.readcsvSICC(datafiles)

    idvData = Utils.GetIdvNameAndData(datafromCsvDIct)

    if idvData != None:
        assert True

    assert False


def test_get_idv_sicc_pairs():
    path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\EMR_8PRF_EMR\\8PRF_H34F00\\SICC_test\\csvSiccData"

    subfolders_site = [f.path for f in os.scandir(path) if f.is_dir()]

    datafromCsvDIct = {}

    for site in subfolders_site:
        datafiles = os.listdir(site)
        for i in range(len(datafiles)):
            datafiles[i] = os.path.join(site, datafiles[i])

        datafromCsvDIct = Utils.readcsvSICC(datafiles)

    idvData = Utils.GetIdvNameAndData(datafromCsvDIct)
    pairs = Utils.get_idv_sicc_pairs(datafromCsvDIct, idvData)

    if pairs != None:
        assert True
    assert False
