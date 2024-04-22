import os
from paddleocr import PaddleOCR
from coams.logging import logger
from coams.excel import *
from coams.RMMS import TCDocumnetImage
from coams.MCOAMS import FetchDB
import argparse
from pdf2image import convert_from_bytes
from coams.tctext import change_metric
from coams.tcconfig import Constants, Query

# define argparse
parser = argparse.ArgumentParser()
parser.add_argument("--pdf_dir", required=True)
parser.add_argument("--output_dir", required=True)
parser.add_argument("--bp_code", required=True)
parser.add_argument("--material_code", required=True)
parser.add_argument("--img_path", required=True)
args = parser.parse_args()

C= Constants()
Q = Query()
E = Error()

dbobj = FetchDB(*C.DB_INFO)

def TCRMMS(pdf_dir, output_dir, bp_code, mat_code, img_path, logger, db):
    bp_mat = bp_code +"_" + mat_code
    output_param = 0
    _, res = db.select_query(Q.file_type_select(bp_math))
    page_code = res[0][0]
    if (bp_mat in C.ENGLISH_MODEL) or (bp_mat in C.KOREAN_MODEL):
        ocr = PaddleOCR(cpu_threads=1, use_angle_cls=True, lang='en', show_log=False)
        logger.add_log("Language : English", debug=True)
    else:
        ocr = PaddleOCR(cpu_threads=1, use_angle_cls=True, lang='ch', show_log=False)
        logger.add_log("Language : Chinese", debug=True)  
    
    imgs = convert_from_bytes(
        open(pdf_dir, 'rb').read(),
        500, 
        grayscale = True,
        size =(2450, None),
        popller_path = C.POPPLER_PATH,
    )
    logger.add_log(f"Number of Pages: {len(imgs)}")
    logger.add_log(f"Multiple Lot: {page_code==3}")

    lots, results, dfs, tc_doc_imgs =[], [], [], []
    
    for i in range(len(imgs)):
        # Loop through pages
        logger.add_log(f"{i+1} page")
        img = imgs[1]
        has_roi = False
        if page_code ==3: page_num =1 
        else: page_num =1 
            
        try:
            DocImg = TCDocumnetImage(
                db, 
                bp_mat,
                pdf_dir,
                img,
                img_path,
                ocr, 
                page_num)
            has_roi = 





