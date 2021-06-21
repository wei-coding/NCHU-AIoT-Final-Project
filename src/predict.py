import librosa
import numpy as np
import random
import os
import time
import json
os.environ['CUDA_VISIBLE_DEVICES'] = "-1"
import tensorflow as tf
import simpleaudio as sa

moods = ['scary', 'happy', 'sad', 'angry', 'No']
genres = [
    "blues",
    "classical",
    "country",
    "disco",
    "hiphop",
    "metal",
    "pop",
    "reggae",
    "rock",
]
mood_prob = {'total': 5}
given_mood_prob = {}
random.seed(time.time())

def get_x(path):
    data = np.zeros((1, (128), 33), dtype=np.float64)
    hop_length = 512
    y, sr = librosa.load(path)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length, n_mfcc=13)
    spectral_center = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=hop_length)
    data[0, :, 0:13] = mfcc.T[0:128, :]
    data[0, :, 13:14] = spectral_center.T[0:128, :]
    data[0, :, 14:26] = chroma.T[0:128, :]
    data[0, :, 26:33] = spectral_contrast.T[0:128, :]

    return data

def get_predict(model_path, music_path):
    model = tf.keras.models.load_model(model_path)
    x = get_x(music_path)
    y = model.predict(x)
    print(f'y = {y}')
    return [float(y[0, i] * 100) for i in range(9)]

def init_porb():
    for mood in moods:
        mood_prob[mood] = 1
        given_mood_prob[mood] = {'total': 9}
        for g in genres:
            given_mood_prob[mood][g] = 1
    
def training_bayes():
    filelist = os.listdir('../gtzan/_train')
    random.seed(time.time())
    while(True):
        f = random.sample(filelist, 1)
        # play music
        wave_read = sa.wave.open('../gtzan/_train/'+f[0], 'rb')
        wave_obj = sa.WaveObject.from_wave_read(wave_read)
        wave_obj.play()

        genre = f[0].split('.')[0]
        for i, m in enumerate(moods):
            print(i, m)
        idx = int(input())
        sa.stop_all()
        mood_prob['total'] += 1
        mood_prob[moods[idx]] += 1
        given_mood_prob[moods[idx]]['total'] += 1
        given_mood_prob[moods[idx]][genre] += 1
        save_model('model')

def save_model(path):
    with open(path, 'w', newline='') as f:
        json.dump(mood_prob, f)
        f.write('\n')
        json.dump(given_mood_prob, f)

def load_model(path):
    global mood_prob, given_mood_prob
    with open(path, 'r') as f:
        lines = f.readlines()
        mood_prob = json.loads(lines[0])
        given_mood_prob = json.loads(lines[1])

def recommend_music(mood: int):
    load_model('../models/bayse_model')
    max_prob = 0.0
    selected_genre = 'blues'
    f = open('../statics/music/data.json')
    song_data: dict = json.load(f)
    f.close()
    if mood == -1:
        # randomize all music
        print('random mode')
        selected_song = random.sample(song_data.keys(), 1)[0]
        return selected_song, None
    print(given_mood_prob[moods[mood]])
    for g, p in given_mood_prob[moods[mood]].items():
        if g == 'total':
            continue
        if p > max_prob:
            max_prob = p
            selected_genre = g
    print('genre =', selected_genre)
    # select song with {candidate} genre
    all_fit_song = []
    for song, genre in song_data.items():
        maxi = np.argmax(genre)
        if selected_genre == genres[maxi]:
            all_fit_song.append(song)
    if len(all_fit_song) > 0:
        selected_song = random.sample(all_fit_song, 1)[0]
    else:
        # search for top 3
        songs = []
        probs = []
        for song, genre in song_data.items():
            songs.append(song)
            probs.append(genre[genres.index(selected_genre)])
        selected_song = select_with_prob(songs, probs, 1)[0]
        print(selected_song)

    return selected_song, selected_genre
    
def select_with_prob(labels: list, probs: list, n: int):
    section = [0]
    for i in range(len(probs)):
        section.append(section[i] + probs[i])
    print(section)
    res = []
    for _ in range(n):
        place = random.random()
        for i in range(len(labels)):
            if place > section[i] and place <= section[i +  1]:
                res.append(labels[i])
    return res


if __name__ == '__main__':
    # init_porb()
    # load_model('model')
    # training_bayes()
    pass