import pyttsx3

engine = pyttsx3.init()

voices = engine.getProperty("voices")

print("Найдено голосов:", len(voices))

for i, voice in enumerate(voices):
    print(i, voice.name)
    print("   ID:", voice.id)