import librosa
import numpy as np
import os
os.environ['CUDA_VISIBLE_DEVICES'] = "-1"
import tensorflow as tf

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
