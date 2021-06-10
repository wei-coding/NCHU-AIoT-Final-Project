from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import predict
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1000 * 1000     # max file 32MB

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploader', methods=['POST'])
def uploader():
    if request.method == 'POST':
        f = request.files['file']
        _, extname = os.path.splitext(f.filename)
        
        # make dir if we do not have data folder
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # generate random string to handle the filename which has some characters not in UTF8
        domain = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
        fn = app.config['UPLOAD_FOLDER'] + '/' + ''.join(random.choices(domain, k=10)) + extname
        f.save(fn)

        return jsonify({
            'filename': f.filename,
            'gernes': predict.get_predict('lstm_genre_classifier_lstm.h5', fn)
        })

# this is for static files
@app.route('/statics/<path:path>')
def send_js(path):
    return send_from_directory('statics', path)

if __name__ == '__main__':
    app.run(debug=True)
