from pydantic import BaseModel
from typing import Optional
#Request data models
class FileData(BaseModel):
    name: str
    type: str
    data: str
class GeminiRequest(BaseModel):
    message: Optional[str] =""
    file: Optional[FileData]=None
    mode: Optional[str]=None
    conversation_id:Optional[str]=None