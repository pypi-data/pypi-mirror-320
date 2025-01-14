import ytb_gears


def main():
    client_secret_file = "client_secret.json"
    video_path = "test.mp4"

    if ytb_gears.today_already_uploaded(client_secret_file):
        return

    print(f"即将上传视频: {video_path}")

    ytb_gears.upload(
        video_path,
        client_secret_file,
        "Youtube Gears Test Video",
        "Uploaded by Youtube Gears",
        "ytb-gears",
        "22",
        "unlisted",
    )
