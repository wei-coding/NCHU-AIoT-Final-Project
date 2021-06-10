from flask import Flask, request, render_template, url_for, jsonify, redirect
from werkzeug.utils import secure_filename
import os
import predict

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.join('data')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000 * 1000

filepath = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    global filepath
    if request.method == 'POST':
        f = request.files['file']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        f.save(filepath)
        return redirect(url_for('result'))

@app.route('/getpredict')
def getpredict():
    global filepath
    predict.load_model('lstm_genre_classifier_lstm.h5')
    r = predict.get_predict(filepath)
    print(f'result is {r}')
    return jsonify(r)

@app.route('/result')
def result():
    return render_template('charts.html')

if __name__ == '__main__':
    app.run(debug=True)