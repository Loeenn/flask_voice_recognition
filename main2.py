import whisper
from datetime import datetime,timedelta
import re
from pymystem3 import Mystem
import pyaudio
import wave
def detect_defects(strin):
    defects = {"стирание краска":0,
                   "сминание":0,
                   "изгибание":0,
                   "нарушение целостность дорожный знак":0,
                   "вандализм":0,
                   "перекрытие растительность":0,
                   "снежный налет":0,
                   "ремонт":0,
                   "разрушение":0,
                   "продольный трещина":0,
                   "яма":0,
                   "трещина поперечный":0,
                   "стирание разметки":0,
                   "размытие пешеходный переход":0,
                   "разрушение бордюрный камень":0,
                   "железная балка":0,
                   "бетонный люк":0,
                   "железный забор":0,
                   "тросовый забор":0,
                   "поперечный трещина":0}
    strin = strin.lower()
    strin = " ".join(strin.split())
    for i in defects.keys():
        if i in strin:
                defects[i] += 1
    return max(defects, key=defects.get)



def speech_recognition (fpath):
    model='base'
    speech_model = whisper.load_model(model)
    result = speech_model. transcribe(fpath)
    return result['text']

def get_date(strin):
    month_dict = {
        1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель', 5: 'май',
        6: 'июнь', 7: 'июль', 8: 'август', 9: 'сентябрь', 10: 'октябрь',
        11: 'ноябрь', 12: 'декабрь'
    }
    def extract_numbers(s):
        return [int(num) for num in re.findall(r'\d+', s)]
    nums = extract_numbers(strin)
    day = None
    month = None
    year = None
    try:
        day = nums[0]
        year = nums[1]
    except:
        day = 1
        year = 2024
    
    for month_number, month_name in month_dict.items():
        if month_name in strin:
            month = month_number
    if month is None:
        month = 2
    if "завтра" in strin:
            day = datetime.now().day
            month = datetime.now().month
            year = datetime.now().year
            day+=1
    if "конец месяц" in strin:
            day = datetime.now().day
            month = datetime.now().month
            year = datetime.now().year
            month+=1
    if "неделя" in strin:
            day = datetime.now().day
            month = datetime.now().month
            year = datetime.now().year
            day+=7
    date = str(day)+"."+str(month)+"."+str(year)
    return date

def preprocess_text(text):
    mystem = Mystem() 
    tokens = mystem.lemmatize(text.lower())
    text = " ".join(tokens)
    
    return text

def all(fpath):
    strin = speech_recognition(fpath)
    strin =  " ".join(strin.split())
    strin = preprocess_text(strin)
    print(strin)
    date = get_date(strin)
    detect = detect_defects(strin)
    return {"date":date,"text":strin,"defects":detect}


# Параметры записи
FORMAT = pyaudio.paInt16  # Формат аудио
CHANNELS = 1  # Количество каналов
RATE = 44100  # Частота дискретизации
CHUNK = 1024  # Размер блока
RECORD_SECONDS = 10  # Длительность записи в секундах
WAVE_OUTPUT_FILENAME = "output.wav"  # Имя файла для сохранения

# Инициализация PyAudio
audio = pyaudio.PyAudio()

# Открытие потока для записи
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Recording...")

frames = []

# Запись данных в список frames
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Finished recording.")

# Остановка и закрытие потока
stream.stop_stream()
stream.close()
audio.terminate()

# Сохранение записи в файл
wf = wave.open("uploads/WAVE_OUTPUT_FILENAME", 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(audio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()


print(all("output.wav"))