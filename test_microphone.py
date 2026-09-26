import sounddevice as sd

print("Доступные микрофоны:")
print(sd.query_devices())