import base64
import os
from google.genai import types
UPLOAD_DIR ="uplods"
os.makedirs(UPLOAD_DIR,exist_ok=True)
def save_file(file_data):
    """decode and save the uploaded file."""
    file_bytes = base64.b64decode(file_data.data)
    safe_name = os.path.basename(file_data.name)
    file_path = os.path.join(UPLOAD_DIR,safe_name)
    with open(file_path,"wb") as file:
        file.write(file_bytes)
        return{
            "file_name": safe_name,
            "file_path": file_path,
            "file_type": file_data.type,
            "file_size": len(file_bytes)
        }
def create_file_part(file_data):
    """ convert base64 file data into a gemini-compatible part."""
    file_bytes =base64.b64decode(file_data.data)
    mime_type = file_data.type or"application/octet-stream"
    return types.Part.from_bytes(
        data = file_bytes,
        mime_type = mime_type
)
                            