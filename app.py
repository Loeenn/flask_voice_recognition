from flask import Flask, request, jsonify, render_template
import whisper
from datetime import datetime
import re
from pymystem3 import Mystem
import pyaudio
import wave
import os

app = Flask(__name__)

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
    print({"date":date,"text":strin,"defects":detect})
    return {"date":date,"text":strin,"defects":detect}


@app.route('/')
def index():
    result = all("uploads/audio.wav")
    return render_template('index.html',**result)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = os.path.join('uploads', file.filename)
        file.save(filename)
        result = all("uploads/"+str(file.filename))
        return render_template('index.html',**result)
        # result = all(filename)
        # return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)