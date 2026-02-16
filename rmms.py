import pytesseract as tess
import pandas as pd
import cv2

# 사용자 정의 모듈 (기존 시스템 구조 유지)
from mcoams.MCOAMS import DocumentImage
from mcoams.logging import logger
from mcoams.image import crop_image, erase_lines
from mcoams.tctext import text_postprocessing
from mcoams.tcconfig import Constants, Query, Error

class TCDocumentImage(DocumentImage):
    def __init__(self, db, bp_id, PDF_PATH, img, img_path, ocr_engine, page):
        super().__init__(db, bp_id, PDF_PATH, img, img_path, ocr_engine, page)
        self.lots = []
        self.results = []
        self.dfs = []
        self.C = Constants()
        self.Q = Query()
        self.E = Error()

    def _read_key_data(self, key="LOT_VAL"):
        """대상 위치를 찾지 않고 키 데이터를 읽는 함수"""
        logger.add_log(f"Reading {key} data")
        
        # ROI 데이터 확인 
        lotvalroi_data = self.check_roi_data(key)
        if lotvalroi_data.empty:
            return False
        
        lotvalroi = lotvalroi_data.values[0]
        if lotvalroi is None:
            return False

        # 이미지 크롭 및 OCR 수행 
        lot_img = crop_image(self.img, lotvalroi)
        lot_text = self.conduct_ocr(lot_img)

        if len(lot_text) > 0:
            if self.bp_id == "SAMPLE_MODEL_A":  
                self.lots = [i[1][0].replace("0", "0") for i in lot_text]
            else:
                self.lots = [i[1][0] for i in lot_text] [cite: 13]
            return True
        return False

    def _read_block(self, img, isvar=0):
        """이미지 블록에서 텍스트 데이터를 읽어 프레임으로 반환"""
        # 언어 설정 분기 (한국어/영어) [cite: 13]
        if (self.bp_id in self.C.KOREAN_MODEL) and (isvar == 1):
            lang_type = "kor_lstm"
        else:
            lang_type = "eng_lstm"

        vars_df = tess.image_to_data(
            img, lang=lang_type, config="--psm 6", output_type='data.frame'
        ).dropna() [cite: 13]

        vars_df['text'] = vars_df['text'].astype(str)
        
        # 문단 및 라인별로 텍스트 결합 [cite: 13]
        return vars_df.groupby(['par_num', 'line_num'])['text'].apply(
            lambda x: " ".join(x)
        ).reset_index(drop=True)

    def get_text(self):
        """이미지 내의 변수(VAR)와 값(VAL) 영역을 읽어 추출"""
        # ROI 이름에 따른 데이터프레임 분리 [cite: 14]
        var_df = self.res[self.res["ROI_NAME"].str.startswith("VAR")].copy()
        val_df = self.res[self.res["ROI_NAME"].str.startswith("VAL")].copy()
        self.dfs = []

        # 특정 모델의 경우 ROI 좌표 미세 조정 [cite: 14]
        if (self.bp_id in self.C.ADJUST_ROI) and not all(lot.isdigit() for lot in self.lots):
            logger.add_log("Reading LOT_VAL data with adjustment")
            lotvalroi_data = self.check_roi_data("LOT_VAL")
            
            if not lotvalroi_data.empty:
                lotvalroi = lotvalroi_data.values[0]
                lotvalroi[1] = lotvalroi[1] + 0.02  # Y축 조정
                lot_img = crop_image(self.img, lotvalroi)
                lot_text = self.conduct_ocr(lot_img)
                if len(lot_text) > 0:
                    self.lots = [i[1][0] for i in lot_text]

            # 변수 및 값 영역 좌표 일괄 조정 [cite: 14]
            var_df["ROI_Y"] += 0.05
            var_df["ROI_X"] -= 0.005
            val_df["ROI_Y"] += 0.05

        # 각 행(Variable-Value 쌍) 처리 [cite: 14]
        for i, row in var_df.iterrows():
            var_roi = (row["ROI_X"], row["ROI_Y"], row["ROI_WIDTH"], row["ROI_HEIGHT"])
            var_cimg = crop_image(self.img, var_roi)
            var_cimg = erase_lines(var_cimg) # 선 제거 전처리 [cite: 14]

            val_name = row["ROI_NAME"].replace("VAR", "VAL")
            val_row = val_df[val_df["ROI_NAME"] == val_name].squeeze()
            
            if not val_row.empty:
                val_roi = (val_row["ROI_X"], val_row["ROI_Y"], val_row["ROI_WIDTH"], val_row["ROI_HEIGHT"])
                val_cimg = crop_image(self.img, val_roi)
                val_cimg = erase_lines(val_cimg)

                # 데이터 추출 및 후처리 [cite: 15]
                df = pd.DataFrame({
                    "var": self._read_block(var_cimg, isvar=1),
                    "val": self._read_block(val_cimg),
                })
                
                df['val'] = df['val'].apply(lambda x: text_postprocessing(self.db, self.bp_id, x, 'VAL'))
                df['var'] = df['var'].apply(lambda x: text_postprocessing(self.db, self.bp_id, x, 'VAR'))
                self.dfs.append(df) [cite: 16]

    def corresponding_lot(self):
        """추출된 데이터를 해당 Lot 번호와 매칭하여 최종 결과 생성"""
        for lot in self.lots:
            # 한국어 모델의 경우 Lot 번호 형식 정리 
            if self.bp_id in self.C.KOREAN_MODEL:
                if len(lot.split('-')[0]) > 8:
                    parts = lot.split('-')
                    lot = parts[0][-8:] + '-' + parts[1]

            content = pd.DataFrame(columns=['var', 'val'])
            # bp_id에서 회사명과 제품명 분리 
            try:
                company, product = self.bp_id.split("_")
            except ValueError:
                company, product = "Unknown", "Unknown"

            base_info = pd.DataFrame({
                'var': ['Company', 'Product', 'Lot_no'],
                'val': [company, product, lot]
            }) [cite: 16]

            content = pd.concat([content, base_info], ignore_index=True)
            dfs = [content] + self.dfs
            self.results.append(pd.concat(dfs, ignore_index=True)) [cite: 16]
