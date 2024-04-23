import pandas as pd
import os

from coams.logging import logger
from coams.MCOAMS import * 
from coams.config import Constants, Query

C = Constants()
Q = Query()

def kinsei(excel_dir):
    if os.path.exists(excel_dir.replace(".pdf", ".xls")):
        excel_dir = excel_dir.replace(".pdf", ".xls")
        logger.add_log(f"Found file {excel_dir}", debug=True)
    elif os.path.exists(excel_dir.replace(".pdf", ".xlsx")):
        excel_dir = excel_dir.replace(".pdf", ".xlsx")
        logger.add_log(f"Found file {excel_dir}")      
    else:
        logger.add_log(f"No such file {excel_dir}")
    try:
        df = pd.read_excel(excel_dir).dropna()
        


def excel_read(excel_dir, copr_id, bp_id, logger):
    output_param =0 
    db = FetchDB(*C.DB_INFO)
    excel_path, excel_name = os.path.split(excel_dir)
    db.delete_data("COA_DOCU", f"DOCU_NAME='{excel_name}'")
    db.commit()
    excel_dir = excel_dir.replace("\\", "/").replace('"', "")
    
    
