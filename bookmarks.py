import json
import os
import requests
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from tqdm import tqdm
import time

def download_media(media_url, save_path, modification_time):
    if os.path.exists(save_path):
        return
    response = requests.get(media_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        # Set the modification time of the downloaded file
        os.utime(save_path, (modification_time, modification_time))
    else:
        print(f"\033[91mFailed to download media from: {media_url}. Reason: {response.reason}\033[0m")

def download_bookmarked_media(json_file, save_directory):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    num_downloaded = 0
    num_failed = 0
    num_total = sum(len(tweet.get("media", [])) for tweet in data)
    
    with tqdm(total=num_total, position=0, leave=True, ncols=100, desc="\033[94mDownloading\033[0m") as progress_bar:
        for tweet in data:
            if "media" in tweet:
                screen_name = tweet["screen_name"]
                created_at = datetime.strptime(tweet["created_at"], "%Y-%m-%d %H:%M:%S %z")
                for media in tweet["media"]:
                    if "original" in media:
                        media_url = media["original"]
                        media_id = tweet["id"]
                        date_string = created_at.strftime("%Y%m%d_%H%M%S")
                        parsed_url = urlparse(media_url)
                        if "video" in media["type"]:
                            file_extension = ".mp4"
                        else:
                            format_param = parse_qs(parsed_url.query).get("format", [""])[0]
                            file_extension = f".{format_param}" if format_param else ""
                        if len(tweet["media"]) > 1:
                            file_name = f"{date_string}_{screen_name}_{media_id}_{media['type']}_{num_downloaded + 1}{file_extension}"
                        else:
                            file_name = f"{date_string}_{screen_name}_{media_id}_{media['type']}{file_extension}"
                        save_path = os.path.join(save_directory, file_name)
                        try:
                            download_media(media_url, save_path, created_at.timestamp())
                            num_downloaded += 1
                        except Exception as e:
                            print(f"\033[91mError downloading media: {e}\033[0m")
                            num_failed += 1
                        finally:
                            progress_bar.update(1)
    
    print(f"\033[92mDownloaded: {num_downloaded}, Failed: {num_failed}, Total: {num_total}\033[0m")

def ascii_animation():
    frames = [
        "Downloading |",
        "Downloading /",
        "Downloading -",
        "Downloading \\"
    ]
    for frame in frames:
        print(frame, end="\r")
        time.sleep(0.2)

if __name__ == "__main__":
    json_file = "bookmarked_tweets.json"  # Path to your JSON file
    save_directory = "downloaded_media"   # Directory where downloaded media will be saved

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    ascii_animation()
    print("\n")

    download_bookmarked_media(json_file, save_directory)
