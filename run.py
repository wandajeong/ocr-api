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
            has_roi = DocImg.get_roi_dat()
        except Exception as e:
            print("Passing this page :" , e)
        # 1 file 1 lot - This can have no lot data at first page
        # 1 file n page n lots 
        # 1 file n page n*m lots 
        if has_roi:
            print("Found ROI Data")
            DocImg.align_image()
            has_key = DocImg._read_key_data("LOT_VAL")
            DocImg.get_text()
            if (page_code !=3):
                lots += DocImg.lots
                results += DocImg.results
                dfs += DocImg.dfs
            elif has_key: # 1 file n or n*m lots 
                DocImg.corresponding_lot()
                tc_doc_imgs.append(DocImg)
            else:
                logger.add_log("Cannot Read Lot...")
                output_param =101
        else:
            logger.add_log("No ROI for this page. passing...")
        # End of loop 
    
     if len(tc_doc_imgs)==0:
         DocImg.lots = lots
         DocImg.results = results
         DocImg.dfs = dfs
         DocImg.corresponding_lot()
         tc_doc_imgs.append(DocImg)
         
     for tc_doc_img in tc_doc_imgs:
         for a file in tc_doc_img.results :
             file_name = "_".join(a_file.iloc[:3,1].tolist()) + ".csv"
             a_file.columns = ['', '']
             if bp_mat in C.KOREAN_MODEL:
                 a_file.to_csv(os.path.join(output_dir, file_name), index=False, encoding='cp949')
             else:
                 a_file.to_csv(os.path.join(output_dir, file_name), index=False)
            
    return output_param

if __name__ == "__main__":
    pdf_dir = args.pdf_dir.replace("\\", "/").replace'"', "").replace('.PDF', '.pdf') 
    output_dir = args.output_dir.replace("\\", "/").replace('"', "")
    if os.path.exists(pdf_dir):
        logger.add_log(f"OCR Starting for {pdf_dir}")
        output = TCRMMS(
            pdf_dir,
            output_dir,
            args.bp_code,
            args.material_code,
            args.img_path,
            logger,
            dbobj
        )
    else:
        outpu=1
        logger.add_log(f"No Such File {pdf_dir}.")
        
    logger.add_log(f"Output : {output}")
    print(output_

    
    




