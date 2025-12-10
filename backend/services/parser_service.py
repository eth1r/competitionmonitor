import base64
from typing import Tuple, Optional
from playwright.async_api import async_playwright
from backend.config import logger, settings

class ParserService:
    async def parse_url(self, url: str) -> Tuple[str, str, str, Optional[str], Optional[str]]:
        """
        Возвращает: (title, h1, paragraph, screenshot_base64, error)
        """
        # Добавляем протокол, если нет
        if not url.startswith("http"):
            url = "https://" + url

        logger.info(f"Запуск браузера для парсинга: {url}")
        
        try:
            async with async_playwright() as p:
                # Запускаем браузер (headless=True значит без окна)
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(user_agent=settings.parser_user_agent)
                
                # Переходим на сайт (ждем максимум timeout секунд)
                try:
                    await page.goto(url, timeout=settings.parser_timeout * 1000)
                except Exception as e:
                    await browser.close()
                    return "", "", "", None, f"Ошибка соединения: {str(e)}"

                # Извлекаем данные
                title = await page.title()
                
                # H1 (первый попавшийся)
                h1 = ""
                if await page.locator("h1").count() > 0:
                    h1 = await page.locator("h1").first.inner_text()
                
                # Первый длинный параграф
                paragraph = ""
                paragraphs = await page.locator("p").all()
                for p_loc in paragraphs:
                    text = await p_loc.inner_text()
                    if len(text) > 50:
                        paragraph = text
                        break
                
                # Скриншот
                screenshot_bytes = await page.screenshot(full_page=False)
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                
                await browser.close()
                return title, h1, paragraph, screenshot_b64, None

        except Exception as e:
            logger.error(f"Критическая ошибка парсера: {e}")
            return "", "", "", None, str(e)

parser_service = ParserService()