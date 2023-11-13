# Import necessary libraries and modules
from flask import Flask, request, jsonify
from flask_cors import CORS
import librosa
import numpy as np
import scipy.signal

# Create a Flask web application instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) for the app
CORS(app)

# Define a route for handling POST requests to '/upload'
@app.route('/upload', methods=['POST'])
def upload_file():
    default_interval = 0.5  # Default time interval
    interval = request.form.get('interval', default=default_interval, type=float)

    # Check if 'file' is present in the request
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    if file:
        # Load the audio from the uploaded file using librosa
        audio, sr = librosa.load(file, sr=None)

        # Apply median filtering to the audio
        audio_filtered = scipy.signal.medfilt(audio, kernel_size=3)

        # Estimate pitch range using librosa
        pitches, magnitudes = librosa.piptrack(y=audio_filtered, sr=sr)
        estimated_pitches = [pitches[:, t].argmax() for t in range(pitches.shape[1])]
        min_pitch, max_pitch = np.percentile(estimated_pitches, [5, 95])

        # Extract pitch data, considering dynamic thresholds
        pitch_data = []
        prev_pitch = 0
        for t in range(0, pitches.shape[1], int(interval * sr)):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]

            # Apply a dynamic threshold to filter out pitch values with minimal changes
            if min_pitch <= pitch <= max_pitch and abs(pitch - prev_pitch) > 0.1 * prev_pitch:
                time = librosa.frames_to_time(t, sr=sr)
                pitch_data.append({'time': time, 'pitch': float(pitch)})
                prev_pitch = pitch

        # Prepare a JSON response with pitch data
        response = {"pitch_data": pitch_data}
        return jsonify(response)

# Run the Flask app if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
