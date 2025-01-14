import pickle
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
    cache_file = Path(client_secret_file).with_suffix(".pickle")
    if cache_file.exists():
        with open(cache_file, "rb") as f:
            credentials: Credentials = pickle.load(f)

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

        with open(cache_file, "wb") as f:
            pickle.dump(credentials, f)

    youtube = googleapiclient.discovery.build(
        "youtube",
        "v3",
        credentials=credentials,
    )

    return youtube
