# YouTube Gears

# Example

```python
import logging

import ytb_gears


def main():
    logging.basicConfig(level=logging.INFO)

    client_secret_file = "client_secret.json"
    video_path = "test.mp4"

    if ytb_gears.today_already_uploaded(client_secret_file):
        return

    print(f"即将上传视频: {video_path}")

    ytb_gears.upload(
        video_path,
        client_secret_file,
        "YouTube Gears Test Video",
        "Uploaded by YouTube Gears",
        "ytb-gears",
        "22",
        "unlisted",
    )


main()
```
