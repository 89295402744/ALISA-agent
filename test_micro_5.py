import sounddevice as sd
import soundfile as sf

print("Говори 5 секунд...")

recording = sd.rec(
    int(5 * 16000),
    samplerate=16000,
    channels=1,
    dtype="float32",
    device=1
)

sd.wait()

sf.write("test_recording.wav", recording, 16000)

print("Готово! Файл test_recording.wav сохранён.")