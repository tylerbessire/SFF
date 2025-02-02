from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FormData(BaseModel):
    accountNumber: Optional[str] = None
    client: Optional[str] = None
    city: Optional[str] = None
    additionalInfo: Optional[Dict] = None

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/manual-entry")
async def manual_entry(form_data: FormData):
    try:
        return {
            "status": "success",
            "data": form_data.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_files(
    input_file: UploadFile = File(...),
    template_file: UploadFile = File(...)
):
    try:
        return {
            "status": "success",
            "message": "Files processed successfully",
            "data": [{
                "accountNumber": "12345",
                "client": "Mock Business",
                "city": "Mock City"
            }]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
