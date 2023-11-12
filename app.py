from flask import Flask, request, jsonify
from flask_cors import CORS
import librosa
import numpy as np
import scipy.signal

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    if file:
        audio, sr = librosa.load(file, sr=None)
        audio_filtered = scipy.signal.medfilt(audio, kernel_size=3)

        # Compute STFT with larger window size
        stft = np.abs(librosa.stft(audio_filtered, n_fft=2048, hop_length=512))

        # Estimate pitches using piptrack
        pitches, magnitudes = librosa.piptrack(S=stft, sr=sr)

        # Extract pitch data and convert to notes
        pitch_data = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                midi_note = librosa.hz_to_midi(pitch)
                note = librosa.midi_to_note(int(round(midi_note)))  # Round to nearest MIDI note and convert to note name
                time = librosa.frames_to_time(t, sr=sr, hop_length=512)
                pitch_data.append({'time': time, 'note': note})

        response = {"pitch_data": pitch_data}
        return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
