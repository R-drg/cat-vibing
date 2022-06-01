import cv2
import numpy as np
import os
from moviepy.editor import *
from yt_dlp import YoutubeDL
import sys
import tweepy
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY=os.environ['CONSUMER_KEY']
CONSUMER_SECRET=os.environ['CONSUMER_SECRET']
ACCESS_TOKEN=os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

# Creation of the actual interface, using authentication
api = tweepy.API(auth)

def post_video(artist, song):
    upload_result = api.media_upload('output.mp4')
    api.update_status(status=artist + " - " + song, media_ids=[upload_result.media_id_string])

# search string on youtube and download mp3
def download_mp3(search_string):

    dl = YoutubeDL({'format': 'bestaudio/best', 'outtmpl': 'temp.mp3', 'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]})
    dl.download(['ytsearch:'+search_string])
    mp3_file = 'temp.mp3'
    return mp3_file

def create_cat_video(artist,album,song):
    video = cv2.VideoCapture("video/cat.mp4")
    os.system('sacad "{0}" "{1}" 1000 temp.jpg'.format(artist, album))
    search_term = artist + " " + song
    found = download_mp3(search_term)
    image = cv2.imread("temp.jpg")
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    out = cv2.VideoWriter('temp.avi', fourcc, 30, (640, 460))
    print("[INFO] Removing green screen...")
    while True:
        ret, frame = video.read()
        if(not ret):
            break
        frame = cv2.resize(frame, (640, 480))
        image = cv2.resize(image, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([0, 180, 0])
        green = np.array([255, 255, 255])
        mask = cv2.inRange(hsv, lower_green, green)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        dilate = cv2.dilate(mask, kernel, iterations=3)
        res = cv2.bitwise_and(frame, frame, mask=dilate)
        f = frame - res
        f = np.where(f == 0, image, f)
        f = f[10:470, 0:640]
        out.write(f)
    out.release()
    videoclip = VideoFileClip("temp.avi").subclip(0, 28)
    audioclip = AudioFileClip("temp.mp3").subclip(28, 56)
    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    print("[INFO] Removing temp files...")
    os.remove("temp.jpg")
    os.remove("temp.avi")
    os.remove("temp.mp3")
    videoclip.write_videofile("output.mp4", audio_codec='aac')



if __name__ == "__main__":
    album = sys.argv[1]
    artist = sys.argv[2]
    song = sys.argv[3]
    create_cat_video(artist,album,song)
    post_video(artist,song)