from pydantic import BaseModel

class Knit2PDFOptions(BaseModel):
    format: str = "mp4"
    outtmpl: str = "videos/%(id)s.%(ext)s"
    writesubtitles: bool = True
