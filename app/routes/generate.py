from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import time
import logging

from app.services.generator import list_models, generate_response, DEFAULT_PARAMS
from app.services.rag import generate_with_rag
from app.templates import templates

ui_router = APIRouter()
api_router = APIRouter(prefix="/api", tags=["api"])

# === UI ===
@ui_router.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    models = list_models()
    context = {
        "request": request,
        "models": models,
        "selected_model": None,
        "prompt": "",
        "prompt_rag": "",
        **DEFAULT_PARAMS,
        "defaults": DEFAULT_PARAMS,
    }
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@ui_router.post("/generate", response_class=HTMLResponse)
async def form_post(
    request: Request,
    model: str = Form(None),
    prompt: str = Form(...),
    max_tokens: int = Form(DEFAULT_PARAMS["max_tokens"]),
    temperature: float = Form(DEFAULT_PARAMS["temperature"]),
    top_p: float = Form(DEFAULT_PARAMS["top_p"]),
    repeat_penalty: float = Form(DEFAULT_PARAMS["repeat_penalty"]),
):
    start = time.time()
    models = list_models()
    try:
        response_text, token_count = generate_response(
            user_input=prompt,
            model_name=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=repeat_penalty
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    duration = round(time.time() - start, 3)
    logging.info(f"UI /generate | model={model} | tokens={token_count} | {duration}s")

    context = {
        "request": request,
        "models": models,
        "selected_model": model,
        "prompt": prompt,
        "prompt_rag": "",  # RAG пустий після LLM submit
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
        "defaults": DEFAULT_PARAMS,
        "response": response_text,
        "tokens": token_count,
        "duration": duration,
    }
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )


@ui_router.post("/generate-rag", response_class=HTMLResponse)
async def form_post_rag(
    request: Request,
    model: str = Form(None),
    prompt: str = Form(...),
    max_tokens: int = Form(DEFAULT_PARAMS["max_tokens"]),
    temperature: float = Form(DEFAULT_PARAMS["temperature"]),
    top_p: float = Form(DEFAULT_PARAMS["top_p"]),
    repeat_penalty: float = Form(DEFAULT_PARAMS["repeat_penalty"]),
):
    start = time.time()
    models = list_models()
    try:
        result = generate_with_rag(
            prompt=prompt,
            model_path=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=repeat_penalty,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    response_text = result.get("answer", "") if isinstance(result, dict) else str(result)
    rag_context = result.get("context", []) if isinstance(result, dict) else []
    tokens = result.get("tokens") if isinstance(result, dict) else None

    duration = round(time.time() - start, 3)
    logging.info(f"UI /generate-rag | model={model} | tokens={tokens} | {duration}s")

    context = {
        "request": request,
        "models": models,
        "selected_model": model,
        "prompt": "",            # LLM пустий після RAG submit
        "prompt_rag": prompt,    # RAG відображає свій prompt
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
        "defaults": DEFAULT_PARAMS,
        "response": response_text,
        "rag_context": rag_context,
        "tokens": tokens,
        "duration": duration,
    }
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context,
    )
