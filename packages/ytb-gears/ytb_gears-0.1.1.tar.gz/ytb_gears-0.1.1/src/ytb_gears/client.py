from pathlib import Path

import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.oauth2.credentials import Credentials


def get_youtube(client_secret_file: str):
    """
    获取 YouTube 客户端对象

    :param client_secret_file: 客户端密钥文件路径
    :return: YouTube 客户端对象
    """

    cached = False
    cache_file = Path(client_secret_file)
    cache_file = cache_file.with_stem(f"{cache_file.stem}_cache")

    if cache_file.exists():
        credentials = Credentials.from_authorized_user_file(cache_file)

        if credentials and credentials.valid:
            cached = True

    if not cached:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secret_file,
            scopes=[
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtube.upload",
            ],
        )

        credentials = flow.run_local_server()

        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(credentials.to_json())

    youtube = googleapiclient.discovery.build(
        "youtube",
        "v3",
        credentials=credentials,
    )

    return youtube
