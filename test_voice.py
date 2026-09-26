import pyttsx3

engine = pyttsx3.init()

# Русский голос Microsoft Irina
voice_id = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0"

engine.setProperty("voice", voice_id)

# Скорость речи
engine.setProperty("rate", 250)

print("Веном говорит по-русски...")

engine.say("Привет. ЭТО ЯНДЕКС АЛИСА.")
engine.runAndWait()

print("Проверка завершена.")