# import the necessary packages
from PIL import Image
from pytesseract import Output
from rutermextract import TermExtractor
from scenedetect import FrameTimecode
import os
import pandas as pd
import pytesseract
import argparse
import cv2
import easydict
import json
import time
import gspread
import httplib2
import gspread as gs
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.1/bin/tesseract'
os.chdir("/Users/yerinaaa/Desktop/OCR/localize-text-tesseract")

class API:
    def __init__(self, email_to_share):
        self.scope = ['https://spreadsheets.google.com/feeds',
                      'https://www.googleapis.com/auth/drive']

        self. credentials = ServiceAccountCredentials.from_json_keyfile_name('localization-text-hse-e9c1ec33fcd0.json', self.scope)
        self.client = gs.authorize(self.credentials)
        self.email_to_share = email_to_share
        self.sheet_shared = False

    def write_to_table(self, filename, table):
        try:
            sheet = self.client.open(filename)
        except gs.exceptions.SpreadsheetNotFound:
            sheet = self.client.create(filename)
        if not self.sheet_shared:
            self.sheet_shared = True
            if isinstance(self.email_to_share, list):
                for email in self.email_to_share:
                    sheet.share(email, perm_type='user', role='writer')
            else:
                    sheet.share(self.email_to_share, perm_type='user', role='writer')
        sheet = sheet.sheet1
        sheet.clear()

        if len(table) != 0:
            cell_list = sheet.range(1, 1, len(table), 2)
            for i in range(len(cell_list) // 2):
                for j in range(2):
                    cell_list[i*2 + j].value = table[i][j]
            sheet.update_cells(cell_list)


class LocalizeText:
    def __init__(self, filename = '', email_to_share = None, time_next_frame = 0, min_conf = 0):
        
        self.filename = filename
        
        if email_to_share == None:
            self.save_into_sheet = True
            self.api = API('es.belyak@gmail.com')
        else: 
            self.save_into_sheet = True
            self.api = API(email_to_share)
        
        if time_next_frame > 0:
            self.time_next_frame = time_next_frame
        else:
            self.time_next_frame = 10
            
        if min_conf > 0:
            self.min_conf = min_conf
        else:
            self.min_conf = 75
        

    def find_text(self, frame, table, tc):
        rus_term_extractor = TermExtractor()
        results = pytesseract.image_to_data(frame, lang = 'rus+eng', output_type=Output.DICT)
        words_from_frame = []

        for i in range(0, len(results["text"])):
            text = results["text"][i]
            conf = int(results["conf"][i])

            if conf > self.min_conf and len(text) > 2:
                for term in rus_term_extractor(text, nested = True):
                    words_from_frame.append(term.normalized)
                    
        words = list(set(words_from_frame))
        for k in range(len(words)):
            table.append([words[k], str(tc)])

    
    def run(self):
#         file_tag = open('file_tag.txt', 'w')
        cap = cv2.VideoCapture(self.filename)
        fps_video = int(cap.get(5))
        next_frame = fps_video * self.time_next_frame
        tc = FrameTimecode(timecode = 0, fps = fps_video)
        table = []
    #     tc_next = Timecode(fps, '00.00.00.00')

        ret, frame = cap.read()
        ret = True
        count_all_frames = 0

        self.find_text(frame, table, tc)

        while ret:
            ret, frame = cap.read()
            count_all_frames += 1

            if count_all_frames % next_frame == 0:
                tc = tc + float(self.time_next_frame)
                self.find_text(frame, table, tc)
        if self.save_into_sheet:
            self.api.write_to_table(self.filename, table)