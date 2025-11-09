from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from audio_utils import analyze_youtube_audio

app = FastAPI()

class AnalyzeRequest(BaseModel):
    youtube_url: str

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        result = analyze_youtube_audio(request.youtube_url)
        return {"stages": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
