from datetime import datetime
import os
import pathlib
import cv2

# 로그생성기
class Logging:
    """
    Parameters
    ---------
    logfiledir : path 
        로그 파일 생성 위치 절대경로
    """
    def __init__(self, logfiledir, silent=False, debug=False):
        self.file_name = logfiledir
        self.silent = silent
        self.debug = debug
        
    def add_log(self, text, debug=False):
        if self.silent or (~self.debug and debug):
            pass
        elif self.debug:
            with open(self.filename, "a+", encoding='UTF8') as logfile:
                now= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logfile.write(now + " $ " + str(text) + "\n")
    
    def save_img(self, img, img_name):
        if self.silent: pass
        else:
            img_path = os.path.join(os.path.split(self.filename)[0], "debug_img")
            pathlib.Path(img_path).mkdir(parents=True, exist_ok=True)
            if ~img_name.endswith(".jpg"):
                img_name = img_name+ ".jpg"
            cv2.imwrite(os.path.join(img_path, img_name), img)


logger = Logging("C:/coams/debug.txt", silent=False, debug=True)
            



            
