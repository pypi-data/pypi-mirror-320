import logging
from datetime import datetime, timezone
from typing import Literal

from googleapiclient.http import MediaFileUpload

from .client import get_youtube


logger = logging.getLogger(__name__)


def today_already_uploaded(client_secret_file: str) -> bool:
    """
    检查今天是否已经上传过视频

    :param client_secret_file: 客户端密钥文件路径
    :return: 是否已经上传过视频
    """
    youtube = get_youtube(client_secret_file)

    request = youtube.search().list(
        part="snippet", forMine=True, maxResults=1, order="date", type="video"
    )
    response = request.execute()
    items = response.get("items", [])

    if not isinstance(items, list) or len(items) == 0:
        logger.warning("没有找到视频")
        return False

    video = items[0]
    upload_date = datetime.strptime(
        video["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=timezone.utc)

    today = datetime.now(timezone.utc)

    is_today = (
        upload_date.year == today.year
        and upload_date.month == today.month
        and upload_date.day == today.day
    )

    if is_today:
        logger.info(f"今天已经上传过视频: {video['snippet']['title']}")
        logger.info(f"上传时间: {upload_date}")

    return is_today


def upload(
    video_path: str,
    client_secret_file: str,
    title: str,
    description: str = "",
    tags: list[str] = [],
    category_id: str = "22",
    privacy_status: Literal["public", "unlisted", "private"] = "public",
):
    """
    上传视频

    :param video_path: 视频文件路径
    :param client_secret_file: 客户端密钥文件路径
    :param title: 视频标题
    :param description: 视频简介
    :param tags: 视频关键字
    :param category_id: 视频分类
    :param privacy_status: 隐私权限, public-公开 unlisted-未公开 private-私有
    """
    body = dict(
        snippet=dict(
            title=title,
            description=description,
            tags=tags,
            categoryId=category_id,
        ),
        status=dict(privacyStatus=privacy_status),
    )

    youtube = get_youtube(client_secret_file)

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path),
    )

    response = request.execute()

    logger.info(f"上传成功: {response}")
