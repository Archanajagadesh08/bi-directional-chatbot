import base64
from google.genai import types
def create_file_part(file_data):
    """ convert base64 file data into a gemini-compatible part."""
    file_bytes =base64.b64decode(file_data.data)
    mime_type = file_data.type or"application/octet-stream"
    return types.Part.from_bytes(
        data = file_bytes,
        mime_type = mime_type
)
                            