import argparse
import xml.etree.ElementTree as ET
import os
import EditXML_Utils

def EditXML(tp_path, approval_file, outputPath):

    approvals = EditXML_Utils.ParseApprovalFile(approval_file)

    EditXML_Utils.Edit_XML(approvals,tp_path,outputPath)
    pass



parser = argparse.ArgumentParser()

parser.add_argument('input',help="input TP Name")
parser.add_argument('approval_file', help ='Approval File')
parser.add_argument('output',help="output Directory")

args = parser.parse_args()

tp_path = args.input
approval_file = args.approval_file
outputPath = args.output

EditXML(tp_path, approval_file, outputPath)








