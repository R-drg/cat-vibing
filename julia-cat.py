import cv2
import numpy as np
import sacad
import os
from moviepy.editor import *
from requests import get
from yt_dlp import YoutubeDL


#search string on youtube and download mp3
def download_mp3(search_string):

    dl = YoutubeDL({'outtmpl': 'temp.mp3'})
    dl.download(['ytsearch:'+search_string])
    mp3_file = 'temp.mp3'
    return mp3_file
    

album = input("Enter album name: ")
artist = input("Enter artist name: ")
song = input("Enter song name: ")

video = cv2.VideoCapture("video/cat.mp4")

os.system('sacad "{0}" "{1}" 600 temp.jpg'.format(artist, album))

search_term = artist + " " + song

found = download_mp3(search_term)

print(found)

image = cv2.imread("temp.jpg")
 
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')

out = cv2.VideoWriter('temp.avi',fourcc, 30, (640,460))

while True:
    
    ret, frame = video.read()
    if(not ret):
        break
    frame = cv2.resize(frame, (640, 480))
    image = cv2.resize(image, (640, 480))
 
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    lower_green = np.array([0, 180, 0])
    green = np.array([255,255,255])

    mask = cv2.inRange(hsv,lower_green,green)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4,4))
    dilate = cv2.dilate(mask, kernel, iterations=3)
    res = cv2.bitwise_and(frame,frame, mask = dilate)
    
    f = frame - res
    f = np.where(f == 0, image, f)

    f = f[10:470, 0:640]

    out.write(f)
 
out.release()

videoclip = VideoFileClip("temp.avi").subclip(0,28)

audioclip = AudioFileClip("temp.mp3").subclip(28,56)


new_audioclip = CompositeAudioClip([audioclip])
videoclip.audio = new_audioclip

os.remove("temp.jpg")
os.remove("temp.avi")
os.remove("temp.mp3")

videoclip.write_videofile("output.mp4")