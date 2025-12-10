import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Загружаем переменные из файла .env
load_dotenv()

# 2. Получаем ключ, который мы спрятали
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("API ключ не найден! Проверьте файл .env")

# 3. Настраиваем Gemini
genai.configure(api_key=api_key)

# 4. Выбираем модель (можно 'gemini-1.5-flash' - она быстрая, или 'gemini-1.5-pro' - она умнее)
model = genai.GenerativeModel('gemini-1.5-flash')

# 5. Отправляем запрос
print("Думаю...")
response = model.generate_content("Привет, Gemini! Расскажи короткий интересный факт о программировании.")

# 6. Выводим ответ
print("\nОтвет Gemini:")
print(response.text)