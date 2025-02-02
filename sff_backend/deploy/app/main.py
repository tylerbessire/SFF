from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any
import pandas as pd
import io
from io import BytesIO
import json
import os
import docx
from .models import BusinessInfo, FileUpload, FormData
from .scraper import BusinessScraper
from .pdf_filler import PDFFiller

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/scrape")
async def scrape_business(business_info: BusinessInfo):
    """
    Note: ABC.ca.gov website access is currently restricted. 
    This endpoint will return mock data for testing purposes.
    """
    mock_data = {
        "results": [{
            "license_number": "12345",
            "business_name": business_info.business_name,
            "address": "123 Main St",
            "city": business_info.city,
            "state": "CA",
            "zip": "95814",
            "status": "Active"
        }]
    }
    return mock_data

@app.post("/api/upload")
async def upload_file(
    input_file: UploadFile = File(...),
    template_file: UploadFile = File(...),
    output_path: str = Form(...)
):
    try:
        input_content = await input_file.read()
        template_content = await template_file.read()
        data = []
        
        file_type = input_file.filename.split('.')[-1].lower()
        if file_type == "csv":
            df = pd.read_csv(io.StringIO(input_content.decode('utf-8-sig')))
            data = df.to_dict('records')
        elif file_type in ["xlsx", "xls"]:
            df = pd.read_excel(io.BytesIO(input_content))
            data = df.to_dict('records')
        elif file_type == "docx":
            doc = docx.Document(io.BytesIO(input_content))
            lines = [para.text for para in doc.paragraphs if para.text.strip()]
            if not lines:
                raise HTTPException(status_code=400, detail="Empty DOCX file")
            headers = lines[0].split(',')
            data = [dict(zip(headers, line.split(','))) for line in lines[1:]]
        elif file_type == "txt":
            df = pd.read_csv(io.StringIO(input_content.decode('utf-8-sig')), sep=",")
            data = df.to_dict('records')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
            
        return {
            "success": True,
            "message": f"Successfully processed {len(data)} records",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/api/manual-entry")
async def manual_entry(form_data: FormData):
    try:
        return {
            "status": "success",
            "data": form_data.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-pdf")
async def generate_pdf(
    template_path: str = Form(...),
    data: str = Form(...)
):
    try:
        form_data = json.loads(data)
        pdf_filler = PDFFiller()
        
        # Use the BASE.pdf template from our templates directory
        template_path = os.path.join(os.path.dirname(__file__), "templates", "BASE.pdf")
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = pdf_filler.fill_pdf(form_data, template_path, output_dir)
        
        # Read the generated PDF and return it as a response
        with open(output_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()
            
        filename = os.path.basename(output_path)
        
        # Clean up the generated file
        os.unlink(output_path)
        
        return StreamingResponse(
            BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
