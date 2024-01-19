import cv2
import regex as re
import json
import easyocr
import numpy as np

class Pan_Info_Extractor:
    def __init__(self):
        try:
            import warnings
            warnings.filterwarnings('ignore')
            self.reader = easyocr.Reader(['en'], gpu=False)
        except ImportError:
            print('No module named: easyocr')
        self.datepatn = r'\d+[-/]\d+[-/]\d+'
        self.panpatn = r'([A-Z]){5}([O0-9]){4}([A-Z]){1}'
        self.namepatn = r'([A-Z]+)\s([A-Z]+)\s([A-Z]+)'
        self.fnamepatn = r'([A-Z]+)\s+?'
        self.godpatn = r'([A-Z]+)\s([A-Z]+)\s([A-Z]+)$|([A-Z]+)\s([A-Z]+)$'

    def info_extractor(self, image_path):
        """Function to extract information from the pan card image

        Args:
                ocr_text (list): text from the ocr

        Returns:
                json: Data extracted from pan card image
        """
        self.PAN = 'NAN'
        self.Name = 'NAN'
        self.FatherName = 'NAN'
        self.DOB = 'NAN'
        self.image = image_path

        img = cv2.imread(image_path)
        OCR_text = self.reader.readtext(img, detail=0, width_ths=0.9)

        gov = [i for i, txt in enumerate(OCR_text) if 'GOVT' in txt][0]
        OCR_text = OCR_text[gov + 1:]

        temp_list = []
        for text in OCR_text:
            name = re.search(self.godpatn, text)
            if name:
                temp_list.append(name.group())

        temp = ''
        for i, char in enumerate(self.PAN):
            if i > 4 and i < 9:
                if char == 'O':
                    char = '0'
            temp = temp + char
        self.PAN = temp

        if self.Name == 'NAN' and temp_list:
            self.Name = temp_list[0]
        if self.FatherName == 'NAN' and len(temp_list) > 1:
            self.FatherName = temp_list[1]

        for text in OCR_text:
            if self.PAN == 'NAN' and re.search(self.panpatn, text):
                self.PAN = re.search(self.panpatn, text).group()
                break

        for text in OCR_text:
            if self.DOB == 'NAN' and re.search(self.datepatn, text):
                self.DOB = re.search(self.datepatn, text).group()
                break

        extracted = {
            'Pan_Number': self.PAN,
            'Name': self.Name,
            'Father_Name': self.FatherName,
            'DOB': self.DOB
        }

        #print("Extracted Data:", extracted)
        return extracted
