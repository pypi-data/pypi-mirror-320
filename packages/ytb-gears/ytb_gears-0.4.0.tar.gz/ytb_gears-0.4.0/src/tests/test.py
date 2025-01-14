import logging
import os

import tqdm

import ytb_gears

# 代理设置
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"


def main():
    logging.basicConfig(level=logging.INFO)

    # OAuth2 客户端凭证文件
    client_secret_file = "client_secret.json"
    # 待上传的视频文件
    video_path = "test.mp4"
    # 封面图片文件
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
            # 上传视频的标题
            "YouTube Gears Test Video",
            thumbnail_path,
            # 上传视频的描述
            "Uploaded by YouTube Gears",
            # 上传视频的标签
            ["ytb-gears", "test"],
            # 上传视频的类别
            "22",
            # 上传视频的隐私设置
            "public",
            progress_callback=update_progress,
        )


main()
