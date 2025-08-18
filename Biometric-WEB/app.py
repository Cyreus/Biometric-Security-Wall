import subprocess
from flask import Flask, request, jsonify, render_template,session,redirect,url_for
import os
import librosa
import numpy as np
from tensorflow.keras.models import load_model
from joblib import load
from flask_sqlalchemy import SQLAlchemy
import ipinfo
# import hashlib

app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
audio_model = load_model('models/modelsv3/model_mk3.keras')
label_encoder = load('models/modelsv3/label_encoder.pkl')
scaler = load('models/modelsv3/scaler.pkl')
anomaly_agent = load('anomaly_agent/anomaly_agent.pkl')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    ''
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False
app.secret_key = ''

db = SQLAlchemy(app)



class LogExtract(db.Model):
    __tablename__ = 'Loglar'
    Id = db.Column(db.Integer, primary_key=True)
    ipAdresi = db.Column(db.String(100))
    sehir = db.Column(db.String(100))
    bolge = db.Column(db.String(100))
    ulke = db.Column(db.String(100))
    konum = db.Column(db.String(100))
    organizasyon = db.Column(db.String(200))
    postaKodu = db.Column(db.String(100))
    zamanDilimi = db.Column(db.String(150))
    girisTarihi = db.Column(db.DateTime)

@app.route('/create-log', methods=['POST'])
def create_log():
    data = request.json
    try:
            new_log = LogExtract(
                ipAdresi=data['ip'],
                sehir=data['city'],
                bolge=data['region'],
                ulke=data['country'],
                konum=data['loc'],
                organizasyon=data['org'],
                postaKodu=data['postal'],
                zamanDilimi=data['timezone'],
                girisTarihi=data['timestamp'],
            )

            db.session.add(new_log)
            db.session.commit()
            return jsonify({'message': 'log saved!'}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error occurred: {e}")
        return jsonify({'message': 'an error occurred while saving log.', 'error': str(e)}), 500
@app.route('/')
def index():
    access_token ='c8275e4b30c982'
    client_ip = request.remote_addr
    handler = ipinfo.getHandler(access_token)
    details = handler.getDetails(client_ip)
    details_dict = details.all

    return render_template('index.html', details=details_dict)

@app.route('/login')
def login():
    if 'authenticated' in session and session['authenticated']:
        return render_template('login.html')
    else:
        return redirect(url_for('index'))

@app.route('/check-auth')
def check_auth():
    is_authenticated = session.get('authenticated', False)
    return jsonify(authenticated=is_authenticated)

@app.route('/validation', methods=['POST'])
def validation():
    email = request.form.get('email')
    password = request.form.get('password')
    message_container = request.form.get('messageContainer')

    if email == "eymenbirce@gmail.com" and password == "123456":
        return render_template('panel.html', message_container=message_container)
    else:
        return "Invalid email or password", 401

@app.route('/predict', methods=['POST'])
def predict_audio():
    if 'audio' not in request.files:
        return jsonify(success=False, message="audio file couldn't upload.")
    audio_file = request.files['audio']
    input_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    output_path = os.path.join(UPLOAD_FOLDER, "converted_audio.wav")

    try:
        audio_file.save(input_path)

        converted_file = convert_audio_to_wav_16khz(input_path, output_path)
        if not converted_file:
            return jsonify(success=False, message="audio converting error.")

        features = extract_features(converted_file)
        if features is None:
            return jsonify(success=False, message="Features couldn't extract.")


        features = features.reshape(1, -1)

        is_anomaly = anomaly_agent.predict(features)


        scaled_features = scaler.transform(features)
        predictions = audio_model.predict(scaled_features)
        predicted_class = np.argmax(predictions, axis=1)
        confidence = np.max(predictions)



        if confidence < 0.90:
            return jsonify(success=False, message="unknown.")
        predicted_label = label_encoder.inverse_transform(predicted_class)[0]
        if predicted_label == 'unknown':
            return jsonify(success=False, message="over_unknown.")
        if is_anomaly[0] == -1:
            return jsonify(success=False, message="Anomaly detected.")
        session['authenticated'] = True
        return jsonify(success=True, message=f"{predicted_label}")
    except Exception as e:
        return jsonify(success=False, message=f"{str(e)}")


def extract_features(file_path):
    if file_path is not None:
        try:
            audio, _ = librosa.load(file_path, sr=16000)

            mfcc = librosa.feature.mfcc(y=audio, sr=16000, n_mfcc=45)
            mfcc_mean = np.mean(mfcc.T, axis=0)

            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=16000)
            spectral_centroid_mean = np.mean(spectral_centroid)

            zcr = librosa.feature.zero_crossing_rate(audio)
            zcr_mean = np.mean(zcr)

            mel_spec = librosa.feature.melspectrogram(y=audio, sr=16000)
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            mel_spec_db_mean = np.mean(mel_spec_db)

            features = np.hstack([mfcc_mean, spectral_centroid_mean, zcr_mean, mel_spec_db_mean])

            return features

        except Exception as e:
            print(f"⚠️ Hata oluştu: {e}")
            return None
    return None

def convert_audio_to_wav_16khz(input_file, output_file):
    try:

        command = [
            "ffmpeg",
            "-y",
            "-i", input_file,
            "-ar", "16000",
            "-ac", "1",
            "-b:a", "256k",
            output_file
        ]
        subprocess.run(command, check=True)
        return output_file
    except Exception as e:
        print(f"audio convert error: {e}")
        return None

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
