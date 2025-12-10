from __future__ import annotations

import asyncio
import os
import random
import threading
import time
from datetime import datetime
from typing import Any, Dict, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging

logger = logging.getLogger(__name__)


# In-memory history for demo purposes
_history: List[Dict[str, Any]] = []
_HISTORY_LIMIT = 50
_history_lock = threading.Lock()
_parse_semaphore = asyncio.Semaphore(3)


def _init_driver() -> webdriver.Chrome:
    """Create a headless Chrome driver with lightweight defaults."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,720")
    # Suppress console window and logging for GUI apps
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")  # Only fatal errors
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Ускорение загрузки - отключаем изображения и другие ресурсы
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Отключить изображения
        "profile.default_content_setting_values.notifications": 2,  # Отключить уведомления
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # Дополнительно отключаем изображения
    
    # PyInstaller compatibility: selenium-manager handles driver automatically
    # but we ensure it works in frozen environment
    try:
        # Selenium 4+ uses Service with automatic driver management
        from selenium.webdriver.chrome.service import Service
        import os
        import sys
        
        # Suppress chromedriver console window on Windows
        service_kwargs = {}
        if sys.platform == "win32":
            # Redirect chromedriver output to NUL to prevent console window
            service_kwargs["log_path"] = os.devnull
        
        service = Service(**service_kwargs)
        return webdriver.Chrome(service=service, options=chrome_options)
    except ImportError:
        # Fallback for older selenium versions
        return webdriver.Chrome(options=chrome_options)


def _safe_get(driver: webdriver.Chrome, by: By, value: str, attr: str | None = None) -> str | None:
    try:
        element = driver.find_element(by, value)
        if attr:
            return element.get_attribute(attr) or None
        return (element.text or "").strip() or None
    except Exception:
        return None


def _try_multiple_selectors(driver: webdriver.Chrome, selectors: List[str], attr: str | None = None) -> str | None:
    """Try multiple CSS selectors and return first match."""
    for selector in selectors:
        result = _safe_get(driver, By.CSS_SELECTOR, selector, attr)
        if result:
            return result
    return None


def _extract_page_info(driver: webdriver.Chrome) -> Dict[str, Any]:
    """Extract general information from any webpage."""
    # Try to find title/heading
    title_selectors = [
        "h1", "h2", ".product-title", ".product-name", ".title", 
        "[class*='title']", "[class*='heading']", "[class*='product']"
    ]
    title = _try_multiple_selectors(driver, title_selectors)
    
    # Try to find price
    price_selectors = [
        ".price", ".product-price", "[class*='price']", "[data-price]",
        "span[class*='price']", "div[class*='price']", ".cost", ".amount"
    ]
    price = _try_multiple_selectors(driver, price_selectors)
    
    # Try to find main image
    image_selectors = [
        "img.product-image", "img[class*='product']", "img[class*='main']",
        ".product-gallery img", "picture img", "main img"
    ]
    image_url = _try_multiple_selectors(driver, image_selectors, attr="src")
    
    # Try to find description - более точные селекторы
    description_selectors = [
        ".description", ".product-description", "[class*='description']",
        ".details", ".product-details", "article p", "main p",
        ".content p", ".text p", "[class*='content'] p"
    ]
    description = _try_multiple_selectors(driver, description_selectors)
    
    # Если описание не найдено, попробуем найти основной текстовый контент
    if not description:
        try:
            # Ищем параграфы с текстом (исключая навигацию и футер)
            paragraphs = driver.find_elements(By.CSS_SELECTOR, "main p, article p, .content p, section p")
            for p in paragraphs:
                text = p.text.strip()
                if text and len(text) > 50:  # Минимум 50 символов
                    description = text
                    break
        except:
            pass
    
    # Get page title as fallback
    page_title = driver.title
    
    # Если описание всё ещё пустое, берём первые абзацы из body
    if not description:
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            # Разбиваем на строки и ищем содержательные абзацы
            lines = body_text.split('\n')
            content_lines = []
            for line in lines:
                line = line.strip()
                if len(line) > 30 and not any(skip in line.lower() for skip in ['меню', 'навигация', 'поиск', 'корзина', 'войти']):
                    content_lines.append(line)
                    if len(' '.join(content_lines)) > 200:
                        break
            description = ' '.join(content_lines[:3]) if content_lines else "Описание не найдено"
        except:
            description = "Описание не найдено"
    
    return {
        "title": title or page_title,
        "price": price,
        "image_url": image_url,
        "description": description,
        "page_title": page_title,
    }


def _fallback_payload(url: str) -> Dict[str, Any]:
    """Return a semi-random payload to emulate parsed data."""
    return {
        "url": url,
        "product_name": random.choice(
            ["Leather Tote Aurora", "Heritage Crossbody", "Soho Saddle Bag"]
        ),
        "price": f"{random.randint(180, 520)} USD",
        "image_url": "https://example.com/static/demo-bag.jpg",
        "description": "Premium Italian leather bag with minimalist hardware.",
        "material": random.choice(["Full-grain leather", "Top-grain leather"]),
        "parsed_at": datetime.utcnow().isoformat(),
    }


def parse_competitor_data(url: str) -> Dict[str, Any]:
    """Parse competitor site with Selenium using universal selectors."""
    # Testing stub for controlled delay and deterministic output
    if os.environ.get("TESTING") == "True":
        time.sleep(2)
        return {"url": url, "status": "Test Done"}

    driver = _init_driver()
    try:
        # Устанавливаем timeout для загрузки страницы (30 секунд)
        driver.set_page_load_timeout(30)
        
        # Устанавливаем стратегию загрузки - не ждем всех ресурсов
        # 'eager' - ждем только DOM, не ждем изображения и стили
        try:
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            caps = DesiredCapabilities.CHROME.copy()
            caps['pageLoadStrategy'] = 'eager'
        except:
            pass
        
        # Load the page
        try:
            driver.get(url)
            logger.info(f"Страница загружена: {url}")
        except TimeoutException:
            # Если timeout, пробуем остановить загрузку и продолжить
            logger.warning(f"Timeout при загрузке, пробуем остановить загрузку: {url}")
            try:
                driver.execute_script("window.stop();")
                logger.info("Загрузка остановлена, продолжаем парсинг")
            except:
                logger.error(f"Не удалось остановить загрузку: {url}")
                return {
                    "url": url,
                    "error": "Timeout: страница не загрузилась за 30 секунд",
                    "parsing_status": "failed",
                    "parsed_at": datetime.utcnow().isoformat(),
                }
        
        # Ждем, пока body загрузится (для JS-сайтов)
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            logger.info("Body элемент загружен")
        except TimeoutException:
            logger.warning("Body не загрузился за 10 секунд, продолжаем парсинг")
        
        # Дополнительная задержка для динамического контента
        time.sleep(3)
        
        # Extract information using universal selectors
        page_info = _extract_page_info(driver)
        
        # Build payload with extracted data
        payload = {
            "url": url,
            "product_name": page_info.get("title") or "Не удалось определить",
            "price": page_info.get("price") or "Цена не найдена",
            "image_url": page_info.get("image_url") or "Изображение не найдено",
            "description": page_info.get("description") or "Описание не найдено",
            "page_title": page_info.get("page_title") or url,
            "parsed_at": datetime.utcnow().isoformat(),
            "parsing_status": "success" if page_info.get("title") else "partial"
        }
        
        return payload
        
    except WebDriverException as e:
        logger.error(f"WebDriver ошибка для {url}: {str(e)}")
        return {
            "url": url,
            "error": f"WebDriver ошибка: {str(e)}",
            "parsing_status": "failed",
            "parsed_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Неожиданная ошибка при парсинге {url}: {str(e)}")
        return {
            "url": url,
            "error": str(e),
            "parsing_status": "failed",
            "parsed_at": datetime.utcnow().isoformat(),
        }
    finally:
        try:
            driver.quit()
            logger.info("WebDriver закрыт")
        except Exception as e:
            logger.warning(f"Ошибка при закрытии WebDriver: {str(e)}")


def add_to_history(entry: Dict[str, Any]) -> None:
    with _history_lock:
        _history.insert(0, entry)
        del _history[_HISTORY_LIMIT:]


def get_history() -> List[Dict[str, Any]]:
    with _history_lock:
        return list(_history)


def clear_history() -> None:
    with _history_lock:
        _history.clear()


async def parse_competitor_data_async(url: str) -> Dict[str, Any]:
    """Async wrapper to run blocking Selenium in a thread."""
    async with _parse_semaphore:
        result = await asyncio.to_thread(parse_competitor_data, url)
        add_to_history(result)
        return result

