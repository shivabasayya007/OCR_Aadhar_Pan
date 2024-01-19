from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pan_extractor import Pan_Info_Extractor
from Aadhar_extractor import Aadhar_Info_Extractor
import cv2
import numpy as np
import os

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["OCR"]
pan_collection = db["pan_data"]
aadhar_collection = db["aadhar_data"]

app = FastAPI()
Pan_extractor = Pan_Info_Extractor()
Aadhar_extractor = Aadhar_Info_Extractor()

@app.get('/')
async def home():
    return "OCR for Aadhar and PAN Card Data Extraction"

@app.post("/extract_pan_details_here")
async def Upload_Pan_Here(image: UploadFile = File(...)):
    image_path = f"{image.filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(image.file.read())

    extracted_data = Pan_extractor.info_extractor(image_path)
    os.remove(image_path)
    pan_collection.insert_one({"data": extracted_data})
    return {"data": extracted_data}



@app.post("/extract_Aadhar_deatils_here")
async def upload_Aadhar_here(front_image: UploadFile = File(...), back_image: UploadFile = File(...)):
    front_image_path = f"{front_image.filename}"
    back_image_path = f"{back_image.filename}"

    try:
        with open(front_image_path, "wb") as front_buffer:
            front_buffer.write(front_image.file.read())

        with open(back_image_path, "wb") as back_buffer:
            back_buffer.write(back_image.file.read())

        extracted_data = Aadhar_extractor.info_extractor(front_image=front_image_path, back_image=back_image_path)
        os.remove(front_image_path)
        os.remove(back_image_path)
        aadhar_collection.insert_one({"data": extracted_data})
        return {"data": extracted_data,}

    except Exception as e:
        os.remove(front_image_path)
        os.remove(back_image_path)        
        raise HTTPException(status_code=500, detail=str(e))

if __name__=="__main__":
    app.run