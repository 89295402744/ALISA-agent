import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from openai import OpenAI
import pyttsx3
import numpy as np
import time

# ---------- DeepSeek ----------
client = OpenAI(
    api_key="local",
    base_url="http://127.0.0.1:9655/v1"
)


# ---------- Голос Венома ----------
engine = pyttsx3.init()
voice_id = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0"
engine.setProperty("voice", voice_id)
# Скорость речи
engine.setProperty("rate", 220)


# ---------- Микрофон ----------
SAMPLE_RATE = 16000
MICROPHONE = 1

recognizer = sr.Recognizer()

print("АЛИСА запущена.")
print("Говори...\n")


# ---------- Записываем голос ----------
print("АЛИСА слушает...")


# ---------- Настройки распознавания паузы ----------
SAMPLE_RATE = 16000
CHUNK = 1024

SILENCE_THRESHOLD = 0.015
SILENCE_DURATION = 1.2
MAX_RECORDING_TIME = 15


# ---------- Ждём начало речи ----------
while True:
    chunk = sd.rec(
        CHUNK,
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        device=MICROPHONE
    )

    sd.wait()

    volume = np.sqrt(np.mean(chunk ** 2))

    if volume > SILENCE_THRESHOLD:
        break


# ---------- Записываем речь ----------
chunks = [chunk]
start_time = time.time()
silence_start = None

while True:

    chunk = sd.rec(
        CHUNK,
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        device=MICROPHONE
    )

    sd.wait()

    chunks.append(chunk)

    volume = np.sqrt(np.mean(chunk ** 2))

    # Человек говорит
    if volume > SILENCE_THRESHOLD:
        silence_start = None

    # Тишина
    else:
        if silence_start is None:
            silence_start = time.time()

        # Пауза достаточно длинная — фраза закончилась
        elif time.time() - silence_start >= SILENCE_DURATION:
            break

    # Защита от бесконечной записи
    if time.time() - start_time >= MAX_RECORDING_TIME:
        break


# ---------- Сохраняем запись ----------
recording = np.concatenate(chunks)

sf.write(
    "voice.wav",
    recording,
    SAMPLE_RATE
)

print("Фраза закончена. Распознаю...")


# ---------- Распознаём речь ----------
with sr.AudioFile("voice.wav") as source:
    audio = recognizer.record(source)

try:
    text = recognizer.recognize_google(
        audio,
        language="ru-RU"
    )

    print("Ты сказал:", text)

except sr.UnknownValueError:
    print("Не удалось разобрать речь")
    exit()

except sr.RequestError as e:
    print("Ошибка распознавания:", e)
    exit()


# ---------- DeepSeek ----------
print("\nDeepSeek думает...\n")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "system",
            "content": "Ты голосовой помощник по имени АЛИСА. Отвечай естественно, понятно и кратко."
        },
        {
            "role": "user",
            "content": text
        }
    ]
)

answer = response.choices[0].message.content

print("алиса:")
print(answer)


# ---------- Озвучиваем ответ ----------
print("АЛИСА говорит...")

engine.say(answer)
engine.runAndWait()