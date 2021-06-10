import librosa
import numpy as np
import os
os.environ['CUDA_VISIBLE_DEVICES'] = "-1"
import math
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam

input_shape = (128, 33)

model = Sequential()
model.add(LSTM(units=128, dropout=0.05, recurrent_dropout=0.35, return_sequences=True, input_shape=input_shape))
model.add(LSTM(units=32,  dropout=0.05, recurrent_dropout=0.35, return_sequences=False))
model.add(Dense(units=9, activation="softmax"))
model.compile(loss="categorical_crossentropy", optimizer=Adam(learning_rate=1e-5), metrics=["accuracy"])

def load_model(path):
    model.load_weights(path)

genre_list = [
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

def get_x(path):
    data = np.zeros((1, (128), 33), dtype=np.float64)
    hop_length = 512
    print(f'path = {path}')
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

def get_predict(path):
    x = get_x(path)
    y = model.predict(x)
    print(f'y = {y}')
    r = [float(y[0, i] * 100) for i in range(9)]
    data = {'filename': path.split('/')[-1], 'gernes': r}
    return data
