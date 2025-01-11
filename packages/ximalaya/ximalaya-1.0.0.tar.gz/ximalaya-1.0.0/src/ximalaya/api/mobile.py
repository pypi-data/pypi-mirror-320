from datetime import datetime

from ximalaya.client import XimalayaClient, ResponsePaginator
from ximalaya.typing import AlbumComment


def api_album_comment_list(client: XimalayaClient, album_id: int, page_size: int = 50, order: str = 'content-score-desc') -> ResponsePaginator[AlbumComment]:
    client.host = 'mobile.ximalaya.com'
    timestamp = int(datetime.now().timestamp() * 1000)

    return ResponsePaginator(
        client,
        url_path=f'/album-comment-mobile/web/album/comment/list/query/{timestamp}?albumId={album_id}&order={order}&pageSize={page_size}',
        page_name='pageId',
        data_path='data.comments.list'
    )
