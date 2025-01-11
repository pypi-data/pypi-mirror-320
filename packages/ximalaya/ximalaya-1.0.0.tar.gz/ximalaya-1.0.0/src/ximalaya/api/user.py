from ximalaya.client import XimalayaClient, ResponsePaginator
from ximalaya.typing import FollowingInfo, UserBasicInfo, UserDetailedInfo, SubscriptionInfo


def api_user_following(client: XimalayaClient, uid: int, page_size: int = 50) -> ResponsePaginator[FollowingInfo]:
    client.host = 'www.ximalaya.com'

    return ResponsePaginator(
        client,
        url_path=f'/revision/user/following?uid={uid}&pageSize={page_size}&keyWord=',
        data_path='data.followingsPageInfo'
    )


def api_user_basic(client: XimalayaClient, uid: int) -> UserBasicInfo:
    client.host = 'www.ximalaya.com'

    return client.get(f'/revision/user/basic?uid={uid}')['data']


def api_user(client: XimalayaClient, uid: int) -> UserDetailedInfo:
    client.host = 'www.ximalaya.com'

    return client.get(f'/revision/user?uid={uid}')['data']


def api_user_sub(client: XimalayaClient, uid: int, page_size: int = 10) -> ResponsePaginator[SubscriptionInfo]:
    client.host = 'www.ximalaya.com'

    return ResponsePaginator(
        client,
        url_path=f'/revision/user/sub?pageSize={page_size}&keyWord=&uid={uid}',
        data_path='data.albumsInfo'
    )
