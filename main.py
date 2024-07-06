from vosk import Model,KaldiRecognizer,SetLogLevel
import wave
import json
from pydub import AudioSegment
from pathlib import Path
import ru_core_news_md
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer 
import pandas as pd
from pydub import AudioSegment
from pydub.silence import split_on_silence
import noisereduce as nr
import librosa
import soundfile as sf
from pydub import AudioSegment
from pydub.effects import normalize
import nltk

from nltk.corpus import stopwords
from pymystem3 import Mystem
from string import punctuation
from autocorrect import Speller
from datetime import datetime,timedelta
import re
mystem = Mystem() 
russian_stopwords = stopwords.words("russian")
nlp = ru_core_news_md.load()
lemmatizer = WordNetLemmatizer()
#sound_path - ссылка на голосовое, далее в папке создается новый файл если старый не подходит критериям


#определение дефекта из str
def detect_defects(strin):
    file_content = strin.split()
    defects = {"стирание краски":0,
                   "сминание":0,
                   "изгибание":0,
                   "нарушение целостности дорожного знака":0,
                   "вандализм":0,
                   "перекрытие растительностью":0,
                   "снежный налет":0,
                   "ремонт":0,
                   "разрушение":0,
                   "продольная трещина":0,
                   "яма":0,
                   "трещина поперечная":0,
                   "стирание разметки":0,
                   "размытие пешеходного перехода":0,
                   "разрущение бордюрного камня":0,
                   "железная балка":0,
                   "бетонный люк":0,
                   "железный забор":0,
                   "тросовый забор":0}
    for word in file_content:
        if word in defects:
            defects[word] += 1
    return max(defects, key=defects.get)


def preprocess_text(text):
    
    tokens = mystem.lemmatize(text.lower())
    
    text = " ".join(tokens)
    
    return text



def translate_date_to_russian(date_string):
    # Словари для преобразования чисел и месяцев

    month_dict = {
        1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель', 5: 'май',
        6: 'июнь', 7: 'июль', 8: 'август', 9: 'сентябрь', 10: 'октябрь',
        11: 'ноябрь', 12: 'декабрь'
    }
    # Разбиваем строку на составляющие
    datestr = date_string.split()
    day="1"
    month = "1"
    year="24"

    big_numbers_dict = {
    "двадцать первый": 21,
    "двадцать второй": 22,
    "двадцать третий": 23,
    "двадцать четвертый": 24,
    "двадцать пятый": 25,
    "двадцать шестой": 26,
    "двадцать седьмой": 27,
    "двадцать восьмой": 28,
    "двадцать девятый": 29,
    "тридцать первый": 31
}
    numbers={
            "первый": 1,
    "второй": 2,
    "третий": 3,
    "четвертый": 4,
    "пятый": 5,
    "шестой": 6,
    "седьмой": 7,
    "восьмой": 8,
    "девятый": 9,
    "десятый": 10,
    "одиннадцатый": 11,
    "двенадцатый": 12,
    "тринадцатый": 13,
    "четырнадцатый": 14,
    "пятнадцатый": 15,
    "шестнадцатый": 16,
    "семнадцатый": 17,
    "восемнадцатый": 18,
    "девятнадцатый": 19,
    "двадцатый": 20,
    "тридцатый": 30,
    }
    month_dict = {
        1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель', 5: 'май',
        6: 'июнь', 7: 'июль', 8: 'август', 9: 'сентябрь', 10: 'октябрь',
        11: 'ноябрь', 12: 'декабрь'
    }
    pattern = r'\b(' + '|'.join(re.escape(key) for key in big_numbers_dict.keys()) + r')\b'
    # распознаем большие сущности.
    matches = re.findall(pattern, " ".join(datestr))
    if len(matches)==2:
        day = big_numbers_dict[matches[0]]
        year = big_numbers_dict[matches[1]]
    if len(matches) == 1:
        year = big_numbers_dict[matches[0]]
        for i in datestr:
            if i in numbers.keys():
                day = numbers[i]
                break
    for i in datestr:
        if i =="завтра":
            return datetime().now().strftime("%d.%m.%Y")+timedelta(days=1)
        if "до конца месяца" in datestr:
            return datetime().now().strftime("%d.%m.%Y")+timedelta(days=30)
        if i =="неделю":
            return datetime().now().strftime("%d.%m.%Y")+timedelta(days=7)
    for i in datestr:
        if i in month_dict.values():
            month = next((k for k, v in month_dict.items() if v == i), None)
    data = str(day)+"."+str(month)+"."+str(year)
    date_obj = datetime.strptime(data, "%d.%m.%y")

    formatted_date = date_obj.strftime("%d.%m.%Y")
    return formatted_date
            
def get_date(text):
    print(text)
    spell = Speller('ru')
    spell = spell(text)
    strin = preprocess_text(spell)  
    print(strin)      
    return translate_date_to_russian(strin)
    
def recognize(sound_path,model_route):
    p = Path(sound_path)
    wf = wave.open(sound_path,"rb")
    if wf.getnchannels()!=1 or wf.getsampwidth()!=2 or wf.getcomptype()!=None:
        sound = AudioSegment.from_wav(sound_path)
        sound = sound.set_channels(1)
        sound_path = str(p.parent)[1:]+str(p.name)[:-4]+"_compressed"+".wav"
        sound.export(sound_path, format="wav")
    #громкость к 60 дцб
    audio = AudioSegment.from_wav(sound_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(sound_path, format="wav")

    audio = AudioSegment.from_file(sound_path)+7

    normalized_audio = normalize(audio)
    normalized_audio.export(sound_path, format="wav")

    #удаление шумов
    audio_data, sample_rate = librosa.load(sound_path, sr=wf.getframerate())
    reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)
    sf.write(sound_path, reduced_noise_audio, sample_rate)
    #удаление пауз
    audio = AudioSegment.from_file(sound_path)
    chunks = split_on_silence(
        audio,
        # Использовать тишину, если она длится хотя бы 1000 мс (1 секунда)
        min_silence_len=1000,
        # Считать тишиной всё, что тише -16 dBFS
        silence_thresh=-50
    )
    audio_without_pauses = AudioSegment.silent(duration=0)  # Начальный пустой аудиосегмент
    for chunk in chunks:
        audio_without_pauses += chunk


    strin =""
    wf = wave.open(sound_path,"rb")
    model = Model(model_route)
    rec = KaldiRecognizer(model,wf.getframerate())

    while True:
        data = wf.readframes(500)
        if len(data)==0:
            break
        if rec.AcceptWaveform(data):
            rec_text = json.loads(rec.Result())
            strin+= rec_text.get("text")
    date = get_date(strin)
    return {"date":date,"text":strin,"defects":detect_defects(strin)}
                
print(recognize("test_by_council.wav","vosk-model-small-ru-0.22"))