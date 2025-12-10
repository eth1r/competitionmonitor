"""
Открыть Swagger UI в браузере
"""
import webbrowser
import time

print("🚀 Открываю Swagger UI...")
print("📡 URL: http://127.0.0.1:8001/docs")
print("\nЗдесь вы можете:")
print("  ✅ Посмотреть все endpoints")
print("  ✅ Протестировать /analyze_text")
print("  ✅ Протестировать /analyze_image")
print("  ✅ Протестировать /parsedemo")
print("\n⚠️ Примечание: OpenAI API требует прокси из вашего региона")

time.sleep(1)
webbrowser.open("http://127.0.0.1:8001/docs")

print("\n✅ Браузер открыт!")
