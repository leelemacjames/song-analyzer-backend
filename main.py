from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from audio_utils import analyze_youtube_audio

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://prismatic-brioche-348185.netlify.app"] for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    youtube_url: str

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        result = analyze_youtube_audio(request.youtube_url)
        return {"stages": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
