from __future__ import annotations

import json
from typing import Any, Dict

from openai import OpenAI

from backend.config import settings

PROMPT = (
    "You are an expert E-commerce UX/UI Auditor specializing in luxury leather goods. "
    "Your task is to analyze the provided website screenshot and extract specific visual metrics "
    "related to product presentation. Return ONLY a raw JSON object (no markdown formatting) with "
    "the following schema: { 'design_score': (integer, 0-10), 'material_quality_focus': "
    "(float, 0.0-10.0), 'lifestyle_context_score': (float, 0.0-10.0), 'summary': (string) }"
)


class OpenAIService:
    """Service wrapper around AsyncOpenAI for vision analysis."""

    def __init__(self) -> None:
        # Используем синхронный клиент с прокси
        import httpx
        
        http_client = None
        if settings.OPENAI_PROXY:
            # Создаем HTTP клиент с прокси
            http_client = httpx.Client(
                proxies=settings.OPENAI_PROXY,
                timeout=30.0
            )
        
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            http_client=http_client
        )

    def analyze_screenshot(self, base64_image: str) -> Dict[str, Any]:
        image_url = (
            f"data:image/png;base64,{base64_image}"
            if not base64_image.startswith("data:image")
            else base64_image
        )

        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=800,
        )

        content = response.choices[0].message.content or "{}"

        try:
            raw = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON received from OpenAI") from exc

        # Normalize and validate expected fields
        return {
            "design_score": int(raw.get("design_score", 0)),
            "material_quality_focus": float(raw.get("material_quality_focus", 0.0)),
            "lifestyle_context_score": float(raw.get("lifestyle_context_score", 0.0)),
            "summary": str(raw.get("summary", "")),
        }


    def analyze_competitor_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Синхронный анализ данных конкурента"""
        try:
            # Определяем тип страницы
            page_title = parsed_data.get('page_title', '').lower()
            product_name = parsed_data.get('product_name', '').lower()
            price = parsed_data.get('price', 'Не указана')
            
            # Определяем, это страница товара или информационная
            is_product_page = (
                price != 'Не указана' and price != 'Цена не найдена' or
                '₽' in str(price) or '$' in str(price) or 
                'руб' in str(price).lower() or
                'товар' in product_name or 'сумка' in product_name or 
                'изделие' in product_name
            )
            
            is_info_page = any(keyword in page_title or keyword in product_name for keyword in [
                'производство', 'о нас', 'about', 'контакт', 'доставка', 
                'оплата', 'гарантия', 'история', 'компания'
            ])
            
            # Формируем текст для анализа
            analysis_text = f"""
Анализируемый сайт конкурента:

URL: {parsed_data.get('url', 'Не указан')}
Заголовок страницы: {parsed_data.get('page_title', 'Не указан')}
Название/Заголовок: {parsed_data.get('product_name', 'Не указано')}
Цена: {price}
Описание: {parsed_data.get('description', 'Не указано')}
Материал: {parsed_data.get('material', 'Не указан')}

Тип страницы: {'Информационная страница (производство, о компании и т.д.)' if is_info_page else 'Страница товара' if is_product_page else 'Каталог или общая страница'}
"""

            # Используем уже созданный клиент
            
            prompt = """Ты - эксперт по анализу сайтов конкурентов в сфере кожаных изделий.

ВАЖНО: Анализируй страницу в контексте её типа:
- Если это ИНФОРМАЦИОННАЯ страница (производство, о компании) - НЕ критикуй отсутствие цены, это нормально
- Если это страница ТОВАРА - анализируй цену, описание товара, характеристики
- Если это КАТАЛОГ - анализируй структуру, навигацию, представление товаров

Верни JSON с анализом:

{
    "page_type": "product|info|catalog",
    "strengths": ["сильная сторона 1", "сильная сторона 2", "сильная сторона 3"],
    "weaknesses": ["слабая сторона 1", "слабая сторона 2"],
    "unique_offers": ["уникальное предложение 1", "уникальное предложение 2"],
    "recommendations": ["рекомендация 1", "рекомендация 2", "рекомендация 3"],
    "summary": "Краткое резюме анализа"
}

Правила:
1. НЕ критикуй отсутствие цены на информационных страницах
2. НЕ критикуй отсутствие характеристик товара на страницах "О компании" или "Производство"
3. Анализируй контент в контексте назначения страницы
4. Будь конкретен и практичен
5. Пиши на русском языке"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": analysis_text}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            content = response.choices[0].message.content or "{}"
            
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                return {
                    "error": True,
                    "note": "Ошибка парсинга ответа OpenAI"
                }
                
        except Exception as e:
            return {
                "error": True,
                "note": f"Ошибка OpenAI API: {str(e)}"
            }

    def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """Анализ изображения"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Проанализируй это изображение товара конкурента. Опиши сильные и слабые стороны презентации товара."},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=500
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"Ошибка анализа изображения: {str(e)}"
            }


openai_service = OpenAIService()