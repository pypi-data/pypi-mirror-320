# YouTube Gears

A Python package for uploading videos to YouTube.

# Service Setup

- <https://console.cloud.google.com/apis/library>
  - YouTube Data API v3
- <https://console.cloud.google.com/apis/credentials>
  - OAuth 2.0 Client ID
    - Application type: Desktop App
    - Download the client secret file (JSON)

# Example

```python
import logging

import tqdm

import ytb_gears


def main():
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("ytb_gears").setLevel(logging.INFO)

    client_secret_file = "client_secret.json"
    video_path = "test.mp4"
    thumbnail_path = "thumbnail.jpg"

    if ytb_gears.today_already_uploaded(client_secret_file):
        return

    print(f"即将上传视频: {video_path}")

    with tqdm.tqdm(total=100) as pbar:

        def update_progress(progress: float):
            pbar.update(int(progress * 100) - pbar.n)

        ytb_gears.upload(
            video_path,
            client_secret_file,
            "YouTube Gears Test Video",
            thumbnail_path,
            "Uploaded by YouTube Gears",
            ["ytb-gears", "test"],
            "22",
            "unlisted",
            progress_callback=update_progress,
        )


main()
```

# Proxy

```python
import os

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
```
