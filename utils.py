from pytube import YouTube, Search
from pytube.cli import on_progress

from datetime import datetime
import logging
import os
import ffmpeg

def start_logging(to_file= True, level=logging.INFO):
    """
    function to start logging to a file

    :param to_file: whether to log to a file or not (else to terminal)
    :param level: logging level (logging.INFO, DEBUG, WARNING, etc.)
    """
    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    filename = f"{logs_folder}/socialEngine_{timestamp}.log"

    if to_file:
        logging.basicConfig(
            filename=filename,
            encoding='utf-8',
            level=level,
            format='[%(asctime)s.%(msecs)03d] %(levelname)s:%(name)s:%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        logging.basicConfig(
            level=level,
            format='[%(asctime)s.%(msecs)03d] %(levelname)s:%(name)s:%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

def download_video(url, output_path, max_length=10, verbose=False):
    """
    function to download a YouTube video

    :param url: url of the video
    :param output_path: path to save the video
    :param max_length: maximum length of the video in minutes
    :param verbose: whether to show moviepy progress bar or not
    """
    # if output_path doesn't exist, create it
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    try:
        # Create a YouTube object
        video = YouTube(url, on_progress_callback=on_progress)

        if video.length > max_length*60:
            logging.warning(f"Video length is greater than {max_length} minutes (skipping...)")
            return

        # Get 1080p resolution video stream
        stream = video.streams.filter(res="1080p").first()

        # If 1080p resolution is not available, get the next best resolution
        if stream is None:
            stream = video.streams.get_highest_resolution()
            # Download the video + audio in 1 (just lower resolution - max 720p)
            stream.download(output_path)
            logging.info(f"video: \"{video.title}\" downloaded successfully (progressive mode)")
        else:
            # get audio for video
            audio = video.streams.get_audio_only()
            # Download the audio
            audio.download(output_path, filename=f"temp_sound_{video.title}.mp4")
            logging.info(f"audio: \"{video.title}\" downloaded")
            
            stream.download(output_path, filename=f"temp_{video.title}.mp4")
            logging.info(f"video: \"{video.title}\" downloaded")

            # ffmpeg way
            ff_video = ffmpeg.input(f"{output_path}/temp_{video.title}.mp4")
            ff_audio = ffmpeg.input(f"{output_path}/temp_sound_{video.title}.mp4")
            ffmpeg.output(ff_video, ff_audio, f"{output_path}/{video.title}.mp4", codec='copy').overwrite_output().run(quiet=True)
            logging.info(f"video \"{video.title}\" merged with audio successfully")

            # delete temp files
            os.remove(f"{output_path}/temp_{video.title}.mp4")
            os.remove(f"{output_path}/temp_sound_{video.title}.mp4")

    except Exception as e:
        logging.error(f"Error downloading video: {str(e)}")

def search_and_get_links(query, n):
    """
    function to search YouTube and get links of top n videos

    :param query: search query
    :param n: number of videos to be returned
    """
    # Search for videos
    search_results = Search(query).results

    # Get the top n video links
    video_links = [result.watch_url for result in search_results[:n]]
    logging.info(f"Found {len(video_links)} videos for the query: {query}")

    return video_links

