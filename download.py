import re
from pytube import Playlist, YouTube
playlist = Playlist('https://www.youtube.com/playlist?list=PLsyOSbh5bs15OXJIigNdRgK0za-JXwhz1')   
DOWNLOAD_DIR = 'music'
playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")    
print(len(playlist.video_urls))    
for url in playlist.video_urls:
    print(url)
    yt=YouTube(url)
    t=yt.streams.filter(only_audio=True).all()
    t[0].download('music')