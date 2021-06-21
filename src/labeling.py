import os
import predict
import json

data = {}
if os.path.exists('../statics/music/data.json'):
    f = open('../statics/music/data.json', encoding='utf-8')
    data = json.load(f)
    f.close()
print(data)

musics = os.listdir('../statics/music')
for i, path in enumerate(musics):
    print(f'running {i}th ...')
    fullpath = os.path.join('../statics/music', path)
    if data.get(path) is None and path != 'data.json':
        pred = predict.get_predict('../models/lstm_genre_classifier_lstm.h5', fullpath)
        data[os.path.splitext(path)[0]] = pred

with open('../statics/music/data.json', 'w') as f:
    json.dump(data, f)