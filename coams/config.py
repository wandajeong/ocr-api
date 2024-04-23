class Constants:
    DB_INFO = ("server_ip", "user_name", "password", "database")
    MODIFIED_VAR = "IS_MODIFIED, M_LOT_NO, M_P_DATE, M_ANALYTE_NAME, M_ANALYTE_VALUE"
    MODIFIED = "0, '', CAST(0 AS DATETIME), '', 0"
    POPPLER_PATH = r"C:/Program Files (x86)/poppler-0.68.0/bin"
    DONOTPROCESS = [] 
    DONOTALIGN =[]
    ALIGNONLY =[]
    ADJUST_ROI =[]
    ENGLISH_MODEL =[]
    KOREAN_MODEL =[]
    MASK_VAL =[]
    PPM_TO_PERCENT =[]
    PERCENT_TO_PPM =[]
    THRES_BIGGER =[]

class Error:
    NORMAL = 'NORMAL'
    
    @staticmethod
    def black_result(file, roi_name):
        return f"OCR Error: {file} / {roi_name} / Blank OCR Result after post processing."

class Query:
    MULTIPLE_RESULT_INSERT =""
    
    @staticmethod
    def coa_docu_input(corp_id, bp_id, file_page, pdf_dir):
        return ""
        
    @staticmethod
    def coa_ocr_result_input(
        corp_id, bp_id, file_page, lot_v, p_date_v, var_v, val_v, is_error
    ):
        return ""    
        
    @staticmethod
    def roi_target_value_select(bp_id, var_v):
        bp_code, mat_code = bp_id.split("_")
        return f"""SELECT ROI_TARGET_VALUE FROM COA_ROI_TARGET 
                WHERE BP_CODE = '{bp_code}' AND 
                MATERIAL_CODE = '{mat_code}' AND 
                ROI_CANDIDATE_VALUE LIKE '%{var_n}%'"""
        
    @staticmethod
    def distinct_vars_select(bp_id):     
        bp_code, mat_code = bp_id.split("_")
        return f"""SELECT DISTINCT ROI_TARGET_VALUE FROM COA_ROI_TARGET
                WHERE BP_CODE = '{bp_code}' AND MATERIAL_CODE = '{mat_code}'"""
        
    @staticmethod
    def file_type_select(bp_id):
        bp_code, mat_code = bp_id.split("_")
        return f"SELECT COA_TYPE FROM BP_MATERIAL WHERE BP_CODE = '{bp_code}' AND MATERIAL_CODE = '{mat_code}'"
        
    @staticmethod
    def roi_data_select(bp_id, page):
        bp_code, mat_code = bp_id.split("_")
        return f"""SELECT COA_ROI FROM BP_MATERIAL 
                WHERE BP_CODE = '{bp_code}' AND MATERIAL_CODE = '{mat_code}' AND DOCU_PAGE={page}"""
        
    @staticmethod
    def history_select(bp_id, file, lot_text):
        return ""

    @staticmethod
    def var_replace_select(bp_id, roi_name):
        bp_code, mat_code = bp_id.split("_")
        return f"""SELECT ROI_TARGET_VALUE FROM COA_ROI_TARGET
                WHERE BP_CODE = '{bp_code}' AND MATERIAL_CODE = '{mat_code}' AND ROI_NAME={roi_name}"""

    @staticmethod
    def bag_select(text):
        return f"SELECT DISTINCT CORRECT_VALUE FROM COA_ANALYTE_BAG WHERE EXTRACT_VALUE = '{text}'"

    
                









    
    
