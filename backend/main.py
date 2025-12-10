from __future__ import annotations

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.schemas import AnalyzeRequest, AnalyzeResponse
from backend.services.history_service import history_service
from backend.services.openai_service import openai_service
from backend.services.parsingservice import (
    parse_competitor_data_async,
    get_history as get_parsing_history,
)
from backend.config import settings


# Rate limiting: защита от злоупотреблений
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Competitor Analysis API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS: Ограничиваем доступ только для локальных клиентов
# Для production добавьте реальные домены в список
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",  # Если используется React/Vue frontend
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "competitor-analysis"}


# === Новые endpoints из оригинального плана ===

from pydantic import BaseModel
from typing import List


class TextAnalysisRequest(BaseModel):
    """Запрос на анализ текста"""
    text: str


class CompetitorAnalysis(BaseModel):
    """Структурированный анализ конкурента"""
    strengths: List[str] = []
    weaknesses: List[str] = []
    unique_offers: List[str] = []
    recommendations: List[str] = []
    summary: str = ""


class TextAnalysisResponse(BaseModel):
    """Ответ на анализ текста"""
    success: bool
    analysis: CompetitorAnalysis | None = None
    error: str | None = None


class ImageAnalysisData(BaseModel):
    """Анализ изображения"""
    description: str = ""
    marketing_insights: List[str] = []
    visual_style_score: int = 5
    visual_style_analysis: str = ""
    recommendations: List[str] = []


class ImageAnalysisResponse(BaseModel):
    """Ответ на анализ изображения"""
    success: bool
    analysis: ImageAnalysisData | None = None
    error: str | None = None


@app.post("/analyze_text", response_model=TextAnalysisResponse)
@limiter.limit("10/minute")  # Максимум 10 запросов в минуту
async def analyze_text(request: TextAnalysisRequest, http_request: Request):
    """
    Анализ текста конкурента
    
    Принимает текст и возвращает структурированную аналитику:
    - Сильные стороны
    - Слабые стороны
    - Уникальные предложения
    - Рекомендации по улучшению стратегии
    """
    try:
        # Промпт для анализа текста
        system_prompt = """Ты — эксперт по конкурентному анализу. Проанализируй предоставленный текст конкурента и верни структурированный JSON-ответ.

Формат ответа (строго JSON):
{
    "strengths": ["сильная сторона 1", "сильная сторона 2", "сильная сторона 3"],
    "weaknesses": ["слабая сторона 1", "слабая сторона 2", "слабая сторона 3"],
    "unique_offers": ["уникальное предложение 1", "уникальное предложение 2", "уникальное предложение 3"],
    "recommendations": ["рекомендация 1", "рекомендация 2", "рекомендация 3"],
    "summary": "Краткое резюме анализа"
}

Важно:
- Каждый массив должен содержать 3-5 пунктов
- Пиши на русском языке
- Будь конкретен и практичен в рекомендациях"""

        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Проанализируй текст конкурента:\n\n{request.text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000
        )
        
        import json
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        
        analysis = CompetitorAnalysis(
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            unique_offers=data.get("unique_offers", []),
            recommendations=data.get("recommendations", []),
            summary=data.get("summary", "")
        )
        
        # Сохраняем в историю
        history_service.add_entry(
            "analyze_text",
            request.text[:200],
            analysis.summary[:500]
        )
        
        return TextAnalysisResponse(
            success=True,
            analysis=analysis
        )
    except Exception as e:
        return TextAnalysisResponse(
            success=False,
            error=str(e)
        )


@app.post("/analyze_image", response_model=ImageAnalysisResponse)
@limiter.limit("10/minute")  # Максимум 10 запросов в минуту
async def analyze_image_endpoint(http_request: Request, file: UploadFile = File(...)):
    """
    Анализ изображения конкурента
    
    Принимает изображение (баннер, сайт, упаковка) и возвращает:
    - Описание изображения
    - Маркетинговые инсайты
    - Оценку визуального стиля
    - Рекомендации
    """
    # Проверяем тип файла
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый тип файла. Разрешены: {', '.join(allowed_types)}"
        )
    
    try:
        # Читаем и кодируем изображение
        import base64
        content = await file.read()
        image_base64 = base64.b64encode(content).decode('utf-8')
        
        # Промпт для анализа изображения
        system_prompt = """Ты — эксперт по визуальному маркетингу и дизайну. Проанализируй изображение конкурента (баннер, сайт, упаковка товара и т.д.) и верни структурированный JSON-ответ.

Формат ответа (строго JSON):
{
    "description": "Детальное описание того, что изображено",
    "marketing_insights": ["инсайт 1", "инсайт 2", "инсайт 3"],
    "visual_style_score": 7,
    "visual_style_analysis": "Анализ визуального стиля конкурента",
    "recommendations": ["рекомендация 1", "рекомендация 2", "рекомендация 3"]
}

Важно:
- visual_style_score от 0 до 10
- Каждый массив должен содержать 3-5 пунктов
- Пиши на русском языке
- Оценивай: цветовую палитру, типографику, композицию, UX/UI элементы"""

        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Проанализируй это изображение конкурента с точки зрения маркетинга и дизайна:"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{file.content_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000
        )
        
        import json
        content_text = response.choices[0].message.content or "{}"
        data = json.loads(content_text)
        
        analysis = ImageAnalysisData(
            description=data.get("description", ""),
            marketing_insights=data.get("marketing_insights", []),
            visual_style_score=data.get("visual_style_score", 5),
            visual_style_analysis=data.get("visual_style_analysis", ""),
            recommendations=data.get("recommendations", [])
        )
        
        # Сохраняем в историю
        history_service.add_entry(
            "analyze_image",
            f"Изображение: {file.filename}",
            analysis.description[:500]
        )
        
        return ImageAnalysisResponse(
            success=True,
            analysis=analysis
        )
    except Exception as e:
        return ImageAnalysisResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/analyze", response_model=AnalyzeResponse)
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        result = await openai_service.analyze_screenshot(request.base64_image)
        return AnalyzeResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - safety net
        raise HTTPException(status_code=500, detail=str(exc)) from exc


DEMO_URL = "https://example.com"


@app.get("/parsedemo")
@limiter.limit("5/minute")  # Максимум 5 запросов в минуту (парсинг медленный)
async def parse_demo(http_request: Request, url: Optional[str] = None, analyze: bool = True) -> dict:
    """
    Парсинг сайта конкурента с опциональным AI анализом
    
    Parameters:
    - url: URL для парсинга
    - analyze: Если True, отправляет данные в OpenAI для анализа (по умолчанию True)
    """
    target_url = url or DEMO_URL
    data = await parse_competitor_data_async(target_url)
    
    # Если парсинг успешен и analyze=True, отправляем в OpenAI
    ai_analysis = None
    if analyze and data.get("parsing_status") in ["success", "partial"]:
        try:
            # Формируем текст для анализа из распарсенных данных
            analysis_text = f"""
Сайт конкурента: {target_url}

Заголовок страницы: {data.get('page_title', 'N/A')}
Название товара/раздела: {data.get('product_name', 'N/A')}
Цена: {data.get('price', 'N/A')}
Описание: {data.get('description', 'N/A')[:500]}
"""
            
            # Отправляем в OpenAI для анализа
            from openai import AsyncOpenAI
            import json
            import httpx
            
            # Настраиваем клиент с прокси, если он указан
            http_client = None
            if settings.OPENAI_PROXY:
                try:
                    transport = httpx.AsyncHTTPTransport(proxy=settings.OPENAI_PROXY)
                    http_client = httpx.AsyncClient(transport=transport, timeout=30.0)
                except Exception as proxy_error:
                    print(f"⚠️ Ошибка настройки прокси: {proxy_error}")
                    print("Попытка подключения без прокси...")
            
            client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                http_client=http_client
            )
            
            system_prompt = """Ты — эксперт по конкурентному анализу. Проанализируй предоставленную информацию о сайте конкурента и верни структурированный JSON-ответ.

Формат ответа (строго JSON):
{
    "strengths": ["сильная сторона 1", "сильная сторона 2", "сильная сторона 3"],
    "weaknesses": ["слабая сторона 1", "слабая сторона 2", "слабая сторона 3"],
    "unique_offers": ["уникальное предложение 1", "уникальное предложение 2"],
    "recommendations": ["рекомендация 1", "рекомендация 2", "рекомендация 3"],
    "summary": "Краткое резюме анализа"
}

Важно:
- Каждый массив должен содержать 2-5 пунктов
- Пиши на русском языке
- Будь конкретен и практичен в рекомендациях
- Анализируй на основе предоставленных данных"""

            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Проанализируй информацию о конкуренте:\n\n{analysis_text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content or "{}"
            ai_analysis = json.loads(content)
            
        except Exception as e:
            # Если анализ не удался, логируем подробную ошибку
            import traceback
            from backend.config import logger
            error_details = traceback.format_exc()
            logger.error(f"AI анализ не удался: {str(e)}")
            logger.debug(f"Детали ошибки:\n{error_details}")
            ai_analysis = {
                "error": str(e), 
                "note": "AI анализ не удался, но парсинг выполнен успешно",
                "hint": "Проверьте OPENAI_API_KEY и OPENAI_PROXY в .env файле"
            }
    
    # Добавляем AI анализ к результатам
    if ai_analysis:
        data["ai_analysis"] = ai_analysis
    
    history_service.add_entry("parsedemo", target_url[:1000], str(data)[:1000])
    return {"url": target_url, "data": data, "history": get_parsing_history()}