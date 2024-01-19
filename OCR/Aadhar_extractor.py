import json

import cv2
import pytesseract
import regex as re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# import easyocr
# READER = easyocr.Reader(['en'])


class Aadhar_Info_Extractor:
    def __init__(self):
        # self.reader = reader
        self.extracted = {}

    def find_adhar_number(self, ocr_text):
        """Function to find adhar number inside the image

        Returns:str: 12 digit aadhaar number
        """
        adhar_number_patn = '[0-9]{4}\s[0-9]{4}\s[0-9]{4}'
        match = re.search(adhar_number_patn, ocr_text)
        if match:
            return match.group()

    def find_name(self, ocr_text):
        """Function to find adhar name inside the image

        Returns:str: name on the aadhar card
        """
        adhar_name_patn = r'\b[A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+$'
        split_ocr = ocr_text.split('\n')
        for ele in split_ocr:
            match = re.search(adhar_name_patn, ele)
            if match:
                return match.group()

    def find_dob(self, ocr_text):
        """Function to find date of birth inside the image

        Returns:str: Date of birth
        """
        dob_patn = '\d+[-/]\d+[-/]\d+'
        yob_patn = '[0-9]{4}'
        DateOfBirth = ''
        if 'DOB' in ocr_text:
            match = re.search(dob_patn, ocr_text)
            DateOfBirth = match.group()
        if 'Year of Birth' in ocr_text:
            match = re.search(yob_patn, ocr_text)
            DateOfBirth = match.group()
        return DateOfBirth

    def find_gender(self, ocr_text):
        """Function to find Gender inside the image

        Returns:
        str: Gender
        """
        if 'Male' in ocr_text or 'MALE' in ocr_text:
            GENDER = 'Male'
        elif 'Female' in ocr_text or 'FEMALE' in ocr_text:
            GENDER = 'Female'
        else:
            GENDER = 'NAN'
        return GENDER

    def find_address(self, backimg):
        """Function to find address inside the image
        Returns:
        str: address on the aadhaar card
        """

        ocr_text = pytesseract.image_to_string(
        backimg, config=f'-l eng --psm 6 --oem 3 ')
        # print(ocr_text)


        try:
            address_start = ocr_text.find('Address')
            address = ocr_text[address_start:]
            pinpatn = r'[0-9]{6}'
            address_end = 0
            pinloc = re.search(pinpatn, address)
            if pinloc:
                address_end = pinloc.end()
            else:
                print('Pin code not found in address')
                address = re.sub('\n', ' ', address[:address_end])
            address = address.split(':')[1]
            return address
        except:
            address = re.sub('\n', ' ', ocr_text)
            pinpatn = re.compile(r'[0-9]{6}')
            pincode = re.search(pinpatn, address)
            # print(pincode.group())
            return pincode.group()


    def info_extractor(self, front_image, back_image):
        """Function to extract information from the aadhaar card image
        Returns:
        json: Data extracted from Adhar photograph
        """
        self.fimage = front_image
        self.bimage = back_image
        self.Name = 'NAN'
        self.Gender = 'NAN'
        self.DateOB = 'NAN'
        self.Aadhar_No = 'NAN'
        self.Address = 'NAN'
        # front image
        img = cv2.imread(self.fimage)
        # OCR_text = self.reader.readtext(img, detail=0,width_ths=0.9)
        OCR_text = pytesseract.image_to_string(img)
        # print(OCR_text)

        self.Aadhar_No = self.find_adhar_number(OCR_text)
        self.Name = self.find_name(OCR_text)
        self.DateOB = self.find_dob(OCR_text)
        self.Gender = self.find_gender(OCR_text)

        # back image
        backimg = cv2.imread(self.bimage)
        backimg = cv2.cvtColor(backimg, cv2.COLOR_BGR2GRAY)
        self.Address = self.find_address(backimg)

        self.extracted = {
        'Aadhar_number': self.Aadhar_No,
        'Name': self.Name,
        'Gender': self.Gender,
        'DOB': self.DateOB,
        'Address': self.Address
        }

        # return self.extracted
        return (self.extracted)
    
if __name__ == '__main__':
    ext = Aadhar_Info_Extractor()
    print(ext.info_extractor('C:/Users/ShivabasayyaB-3225/OneDrive/Desktop/front Aadhar.jpg','C:/Users/ShivabasayyaB-3225/OneDrive/Desktop/BackAadhar_s.jpg'))