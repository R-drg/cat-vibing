import cv2
import numpy as np
import os
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from yt_dlp import YoutubeDL
import sys
from dotenv import load_dotenv

load_dotenv()


# search string on youtube and download mp3
def download_mp3(search_string):
    dl = YoutubeDL(
        {
            "format": "bestaudio/best",
            "outtmpl": "temp",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
    )
    dl.download(["ytsearch:" + search_string])
    mp3_file = "temp"
    return mp3_file


def create_cat_video(artist, album, song):
    video = cv2.VideoCapture("video/cat.mp4")
    os.system('sacad "{0}" "{1}" 1000 temp.jpg'.format(artist, album))
    search_term = artist + " " + song + " audio only"
    download_mp3(search_term)
    image = cv2.imread("temp.jpg")

    # Use album cover dimensions (1000x1000)
    album_height, album_width = image.shape[:2]

    fourcc = cv2.VideoWriter_fourcc("M", "J", "P", "G")
    out = cv2.VideoWriter("temp.avi", fourcc, 30, (album_width, album_height))
    print("[INFO] Removing green screen...")
    while True:
        ret, frame = video.read()
        if not ret:
            break

        # Resize cat video to match album cover size
        frame = cv2.resize(frame, (album_width, album_height))

        # Create green screen mask
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([0, 180, 0])
        green = np.array([255, 255, 255])
        mask = cv2.inRange(hsv, lower_green, green)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
        dilate = cv2.dilate(mask, kernel, iterations=3)

        # Invert mask to get the cat (non-green areas)
        cat_mask = cv2.bitwise_not(dilate)

        # Extract cat from frame
        cat_only = cv2.bitwise_and(frame, frame, mask=cat_mask)

        # Create inverse mask for the album cover
        album_mask = dilate
        album_with_hole = cv2.bitwise_and(image, image, mask=album_mask)

        # Combine album cover with cat on top
        f = cv2.add(album_with_hole, cat_only)

        out.write(f)
    out.release()
    videoclip = VideoFileClip("temp.avi").subclipped(0, 28)
    audioclip = AudioFileClip("temp.mp3").subclipped(28, 56)
    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    print("[INFO] Removing temp files...")
    os.remove("temp.jpg")
    os.remove("temp.avi")
    os.remove("temp.mp3")
    videoclip.write_videofile("output.mp4", audio_codec="aac")


if __name__ == "__main__":
    album = sys.argv[1]
    artist = sys.argv[2]
    song = sys.argv[3]
    create_cat_video(artist, album, song)
