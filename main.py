from utils import search_and_get_links, download_video, start_logging
import logging
from datetime import datetime

if __name__ == '__main__':
    start_logging(to_file=False)

    links = search_and_get_links("subway surfers game play 9:16 short", 3)

    print(links)

    for link in links:
        download_video(link, "videos/stimmy", max_length=35, verbose=True)