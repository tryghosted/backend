import os
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, HTTPException, UploadFile, File
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
import uvicorn

from interview_analyzer.api.api_v1.feedback.endpoint import QuestionAnswerFeedback, QuestionAndAnswer, \
    question_answer_feedback
from interview_analyzer.api.api_v1.speech_to_text.endpoint import LabelledTranscribedText, speech_to_text
from interview_analyzer.app_lifespan_management import init_app_state, cleanup_app_state
from interview_analyzer.utils.standard_logger import get_logger

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_app_state(app.state)
    yield
    await cleanup_app_state(app.state)


app = FastAPI(title="Silver", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    return "I'm healthy, yo!"


@app.post("/api-v1/audioToText/", response_model=LabelledTranscribedText)
async def return_speech_to_text(file: UploadFile, request: Request):
    logger.debug(f"Received request to transcribe audio to text - {file.filename}")
    try:
        result: LabelledTranscribedText = await speech_to_text(audio_file=file, state=request.app.state)
        return result
    except Exception as e:
        logger.error(e)
        return HTTPException(status_code=500)


@app.post("/api-v1/questionAnswerFeedback/", response_model=QuestionAnswerFeedback)
async def return_question_answer_feedback(endpoint_input: QuestionAndAnswer, request: Request):
    logger.debug(f"Received request to provide feedback on question and answer - {endpoint_input}")
    try:
        result: QuestionAnswerFeedback = await question_answer_feedback(
            endpoint_input=endpoint_input,
            state=request.app.state
        )
        return result
    except Exception as e:
        logger.error(e)
        return HTTPException(status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=os.getenv("PORT", 5000))
