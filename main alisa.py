import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from openai import OpenAI
import pyttsx3
import numpy as np


# =========================================================
# DEEPSEEK
# =========================================================

client = OpenAI(
    api_key="local",
    base_url="http://127.0.0.1:9655/v1"
)


# =========================================================
# МИКРОФОН
# =========================================================

SAMPLE_RATE = 16000
MICROPHONE = 1

BLOCK_SIZE = 1024

# Чувствительность определения речи
SILENCE_THRESHOLD = 0.012

# Сколько секунд тишины считать концом фразы
SILENCE_DURATION = 1.2

# Максимальная продолжительность одной фразы
MAX_RECORDING_TIME = 15


# =========================================================
# РАСПОЗНАВАНИЕ РЕЧИ
# =========================================================

recognizer = sr.Recognizer()


# =========================================================
# ГОЛОС АЛИСЫ
# =========================================================

VOICE_ID = (
    r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices"
    r"\Tokens\TTS_MS_RU-RU_IRINA_11.0"
)

VOICE_RATE = 170


# =========================================================
# ПРОСЛУШИВАНИЕ
# =========================================================

def listen():

    print("\nАлиса слушает...")

    frames = []

    started = False
    silence_time = 0
    total_time = 0

    try:

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            device=MICROPHONE,
            blocksize=BLOCK_SIZE
        ) as stream:

            while True:

                data, overflowed = stream.read(BLOCK_SIZE)

                # Определяем громкость звука
                volume = np.sqrt(np.mean(data ** 2))

                if volume > SILENCE_THRESHOLD:

                    # Началась речь
                    started = True
                    silence_time = 0

                elif started:

                    # Пользователь замолчал
                    silence_time += BLOCK_SIZE / SAMPLE_RATE

                # Записываем только после начала речи
                if started:
                    frames.append(data.copy())

                total_time += BLOCK_SIZE / SAMPLE_RATE

                # Пользователь закончил говорить
                if started and silence_time >= SILENCE_DURATION:
                    break

                # Защита от слишком длинной записи
                if total_time >= MAX_RECORDING_TIME:
                    break

    except Exception as e:

        print("Ошибка микрофона:", e)
        return None


    # Если речи не было
    if not frames:

        return None


    # Объединяем записанные куски
    recording = np.concatenate(frames)


    # Сохраняем запись
    sf.write(
        "voice.wav",
        recording,
        SAMPLE_RATE
    )


    print("Фраза закончена. Распознаю...")


    # =====================================================
    # GOOGLE SPEECH-TO-TEXT
    # =====================================================

    try:

        with sr.AudioFile("voice.wav") as source:

            audio = recognizer.record(source)


        text = recognizer.recognize_google(
            audio,
            language="ru-RU"
        )


        print("Ты сказал:", text)

        return text


    except sr.UnknownValueError:

        print("Не удалось разобрать речь.")

        return None


    except sr.RequestError as e:

        print("Ошибка распознавания:", e)

        return None


# =========================================================
# DEEPSEEK
# =========================================================

def ask_deepseek(text):

    print("\nDeepSeek думает...\n")


    try:

        response = client.chat.completions.create(

            model="deepseek-chat",

            messages=[

                {
                    "role": "system",
                    "content": (
                        "Ты голосовой помощник по имени Алиса. "
                        "Отвечай естественно, понятно и кратко."
                    )
                },

                {
                    "role": "user",
                    "content": text
                }

            ]
        )


        answer = response.choices[0].message.content

        return answer


    except Exception as e:

        print("Ошибка DeepSeek:", e)

        return "Произошла ошибка при обращении к DeepSeek."


# =========================================================
# ГОЛОСОВОЙ ОТВЕТ
# =========================================================

def speak(text):

    print("\nАлиса:")
    print(text)

    print("\nАлиса говорит...")


    try:

        # Создаем новый TTS-движок для каждого ответа
        engine = pyttsx3.init()

        engine.setProperty(
            "voice",
            VOICE_ID
        )

        engine.setProperty(
            "rate",
            VOICE_RATE
        )

        engine.say(text)

        engine.runAndWait()

        engine.stop()

        del engine


    except Exception as e:

        print("Ошибка голосового движка:", e)


# =========================================================
# КОМАНДЫ ЗАВЕРШЕНИЯ
# =========================================================

exit_commands = [

    "выход",
    "стоп",
    "завершить работу",
    "заверши работу",
    "закройся",
    "выключись",
    "пока"

]


# =========================================================
# ЗАПУСК АЛИСЫ
# =========================================================

print("================================")
print("        АЛИСА ЗАПУЩЕНА")
print("================================")


while True:

    # Слушаем пользователя
    text = listen()


    # Если речь не распознана
    if not text:

        continue


    # Приводим текст к нижнему регистру
    text_lower = text.lower().strip()


    # =====================================================
    # ПРОВЕРКА КОМАНДЫ ЗАВЕРШЕНИЯ
    # =====================================================

    if any(
        command in text_lower
        for command in exit_commands
    ):

        speak("Хорошо. До встречи.")

        break


    # =====================================================
    # ОТПРАВЛЯЕМ ЗАПРОС В DEEPSEEK
    # =====================================================

    answer = ask_deepseek(text)


    # =====================================================
    # АЛИСА ОТВЕЧАЕТ ГОЛОСОМ
    # =====================================================

    speak(answer)


print("\nАлиса завершила работу.")