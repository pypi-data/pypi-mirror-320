from ximalaya.client import XimalayaClient, ResponsePaginator
from ximalaya.typing import AlbumInfo


def api_category_v2_albums(client: XimalayaClient, category_id: int, page_size: int = 50, sort_by: int = 1) -> ResponsePaginator[AlbumInfo]:
    client.host = 'www.ximalaya.com'

    return ResponsePaginator(
        client,
        url_path=f'/revision/category/v2/albums?pageSize={page_size}&sort={sort_by}&categoryId={category_id}',
        page_name='pageNum',
        data_path='data.albums'
    )
