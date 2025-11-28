# app/schemas/mata_kuliah_schema.py
from pydantic import BaseModel
from typing import Optional

class MataKuliahResponse(BaseModel):
    kode: str
    nama: str
    dosen: str
    sks: Optional[int] = 0
    
    class Config:
        from_attributes = True