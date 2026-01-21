import cv2
import numpy as np
import os
from moviepy import VideoFileClip, AudioFileClip
from yt_dlp import YoutubeDL
import sys
from dotenv import load_dotenv
import musicbrainzngs
import re

load_dotenv()

# Configure MusicBrainz
musicbrainzngs.set_useragent("cat-vibing", "1.0", "your@email.com")


# Search for album name based on artist and song
def search_album(artist, song):
    try:
        print(f"[INFO] Searching for album: {artist} - {song}")
        result = musicbrainzngs.search_recordings(
            artist=artist, recording=song, limit=5
        )

        if result["recording-list"]:
            for recording in result["recording-list"]:
                if "release-list" in recording and recording["release-list"]:
                    for release in recording["release-list"]:
                        if (
                            release["release-group"]["type"] == "Album"
                            or release["release-group"]["type"] == "EP"
                        ):
                            album = release["title"]
                            print(f"[INFO] Found album: {album}")
                            # Remove parentheses and their content from album name
                            album = re.sub(r"\s*\(.*?\)\s*", " ", album).strip()
                            return album

        return song
    except Exception as e:
        print(f"[ERROR] Album search failed: {e}, using song name as fallback")
        return song


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


def create_cat_video(artist, song, album=None):
    # If album is not provided, search for it
    if album is None:
        album = search_album(artist, song)

    video = cv2.VideoCapture("video/cat.mp4")
    os.system('sacad "{0}" "{1}" 1000 temp.jpg'.format(artist, album))
    search_term = artist + " " + song + " audio only"
    download_mp3(search_term)
    image = cv2.imread("temp.jpg")

    # Use album cover dimensions (1000x1000)
    album_height, album_width = image.shape[:2]

    # Define cat size
    cat_scale = 0.7
    cat_width = int(album_width * cat_scale)
    cat_height = int(album_height * cat_scale)

    fourcc = cv2.VideoWriter_fourcc("M", "J", "P", "G")
    out = cv2.VideoWriter("temp.avi", fourcc, 30, (album_width, album_height))
    print("[INFO] Removing green screen...")
    while True:
        ret, frame = video.read()
        if not ret:
            break

        # Resize cat video to smaller size
        frame = cv2.resize(frame, (cat_width, cat_height))

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

        # Start with the full album cover
        f = image.copy()

        # Calculate position for bottom-left corner
        y_offset = album_height - cat_height
        x_offset = 0

        # Create ROI (Region of Interest) in the bottom-left corner
        roi = f[y_offset : y_offset + cat_height, x_offset : x_offset + cat_width]

        # Apply the cat mask to the ROI
        roi_bg = cv2.bitwise_and(roi, roi, mask=dilate)

        # Combine the background ROI with the cat
        roi_combined = cv2.add(roi_bg, cat_only)

        # Place the combined ROI back into the frame
        f[y_offset : y_offset + cat_height, x_offset : x_offset + cat_width] = (
            roi_combined
        )

        out.write(f)
    out.release()

    # Define the duration you want
    duration = 28
    audio_start = 48

    print("[INFO] Loading video and audio clips...")
    videoclip = VideoFileClip("temp.avi").subclipped(0, duration)
    audioclip = AudioFileClip("temp.mp3").subclipped(
        audio_start, audio_start + duration
    )

    print(f"[INFO] Video duration: {videoclip.duration}s")
    print(f"[INFO] Audio duration: {audioclip.duration}s")

    # Set the audio using with_audio method
    final_clip = videoclip.with_audio(audioclip)

    print("[INFO] Writing final video file...")
    final_clip.write_videofile("output.mp4", codec="libx264", audio_codec="aac")

    # Close clips
    final_clip.close()
    audioclip.close()

    print("[INFO] Removing temp files...")
    os.remove("temp.jpg")
    os.remove("temp.avi")
    os.remove("temp.mp3")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python julia-cat.py <artist> <song> [album]")
        sys.exit(1)

    artist = sys.argv[1]
    song = sys.argv[2]
    album = sys.argv[3] if len(sys.argv) > 3 else None

    create_cat_video(artist, song, album)
