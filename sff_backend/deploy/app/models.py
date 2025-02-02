from pydantic import BaseModel
from typing import List, Optional

class BusinessInfo(BaseModel):
    business_name: str
    city: str

class FileUpload(BaseModel):
    file_type: str
    content: str

class FormData(BaseModel):
    account_number: Optional[str] = None
    client: Optional[str] = None
    city: Optional[str] = None
    additional_info: Optional[dict] = None
