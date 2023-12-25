from utils import search_and_get_links, download_video, start_logging
import random
from bing_image_downloader import downloader
import csv
import logging
import time

from moviepy.editor import *

if __name__ == "__main__":
    start_logging(to_file=True)

    file_name = "vs_topics_2.csv"
    out_dir = "vs_shorts_2"

    entries = []
    with open(file_name, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            entries.append(row)

    for row in entries:
        # get two fact / topics
        optionOne = row[0]
        optionTwo = row[1]

        logging.info(f"Creating video for {optionOne} vs {optionTwo}")

        # Set the duration of the video (in seconds)
        video_duration = 8

        # get images for the two options
        downloader.download(
            optionOne,
            limit=1,
            output_dir="images/content",
            adult_filter_off=True,
            force_replace=True,
            timeout=60,
            verbose=False,
        )

        while len(os.listdir(f"images/content/{optionOne}")) == 0:
            downloader.download(
                optionOne,
                limit=1,
                output_dir="images/content",
                adult_filter_off=True,
                force_replace=True,
                timeout=60,
                verbose=False,
            )
            time.sleep(5)

        imageOneName = os.listdir(f"images/content/{optionOne}")[0]
        optionOneImage = f"images/content/{optionOne}/{imageOneName}"

        logging.info(f"Got image for {optionOne}")

        downloader.download(
            optionTwo,
            limit=1,
            output_dir="images/content",
            adult_filter_off=True,
            force_replace=True,
            timeout=60,
            verbose=False,
        )

        while len(os.listdir(f"images/content/{optionTwo}")) == 0:
            downloader.download(
                optionTwo,
                limit=1,
                output_dir="images/content",
                adult_filter_off=True,
                force_replace=True,
                timeout=60,
                verbose=False,
            )
            time.sleep(5)

        imageTwoName = os.listdir(f"images/content/{optionTwo}")[0]
        optionTwoImage = f"images/content/{optionTwo}/{imageTwoName}"

        logging.info(f"Got image for {optionTwo}")

        ### Create the video ###

        # Load the image
        image_path = "images/wur_background.jpg"
        image = ImageClip(image_path)

        # Create a video clip with the image
        video = image.set_duration(video_duration)

        # Add text on the top
        text_top = (
            TextClip(
                optionOne,
                fontsize=80,
                font="mrbeast",
                stroke_width=3,
                stroke_color="black",
                color="white",
            )
            .set_position(("center", 0.03), relative=True)
            .set_duration(video_duration)
        )

        # Add text on the bottom
        bottom_text_start = 2
        text_bottom = (
            TextClip(
                optionTwo,
                fontsize=80,
                font="mrbeast",
                stroke_width=3,
                stroke_color="black",
                color="white",
            )
            .set_position(("center", 0.56), relative=True)
            .set_duration(video_duration - bottom_text_start)
            .set_start(bottom_text_start)
        )

        # add images to video
        optionOneImage = (
            ImageClip(optionOneImage)
            .set_position(("center", 0.1), relative=True)
            .set_duration(video_duration)
            .resize(height=600)
        )

        optionTwoImage = (
            ImageClip(optionTwoImage)
            .set_position(("center", 0.63), relative=True)
            .set_duration(video_duration - bottom_text_start)
            .set_start(bottom_text_start)
            .resize(height=600)
        )

        # have second part where it creates percentage of votes
        voteOne = random.randint(0, 100)
        voteTwo = 100 - voteOne

        result_start_time = 6
        # Add text on the top
        text_vote_top = (
            TextClip(
                str(voteOne) + "%",
                fontsize=90,
                font="mrbeast",
                stroke_width=3,
                stroke_color="black",
                color="white",
            )
            .set_position((0.2, 0.41), relative=True)
            .set_duration(video_duration - result_start_time)
            .set_start(result_start_time)
        )

        # Add text on the bottom
        text_vote_bottom = (
            TextClip(
                str(voteTwo) + "%",
                fontsize=90,
                font="mrbeast",
                stroke_width=3,
                stroke_color="black",
                color="white",
            )
            .set_position((0.2, 0.50), relative=True)
            .set_duration(video_duration - result_start_time)
            .set_start(result_start_time)
        )

        video = CompositeVideoClip(
            [
                video,
                text_top,
                text_bottom,
                optionOneImage,
                optionTwoImage,
                text_vote_top,
                text_vote_bottom,
            ]
        )

        # adding audio
        clockTickAudio = (
            AudioFileClip("audio/clock_tick.mp3")
            .set_duration(result_start_time)
            .set_end(result_start_time)
        )

        dingSound = (
            AudioFileClip("audio/ding.mp3")
            .set_duration(video_duration - result_start_time)
            .set_start(result_start_time)
            .set_end(video_duration)
        )

        video_audio = CompositeAudioClip([clockTickAudio, dingSound])
        video = video.set_audio(video_audio)

        # Write the video to the file
        video.write_videofile(
            f"{out_dir}/{optionOne}_vs_{optionTwo}.mp4", audio_codec="aac", fps=30
        )

        logging.info(f"Created video for {optionOne} vs {optionTwo}")
