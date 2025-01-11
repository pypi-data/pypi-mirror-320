from __future__ import annotations
from typing import TypedDict


class AlbumComment(TypedDict):
    albumId: int
    albumPaid: bool
    albumUid: int
    anchorLiked: bool
    auditStatus: int
    commentId: int
    content: str
    createdAt: int
    isHighQuality: bool
    likeStatus: int
    liked: bool
    likes: int
    nickname: str
    playProgress: int
    recStatus: int
    region: str
    replyCount: int
    smallHeader: str
    uid: int
    updatedAt: int
    userTags: list[UserTag]
    vLogoType: int
    vipIconUrl: str
    vipJumpUrl: str


class AlbumInfo(TypedDict):
    albumId: int
    albumPlayCount: int
    albumTrackCount: int
    albumCoverPath: str
    albumTitle: str
    albumUserNickName: str
    anchorId: int
    anchorGrade: int
    mvpGrade: int
    isDeleted: bool
    isPaid: bool
    isFinished: int
    anchorUrl: str
    albumUrl: str
    intro: str
    vipType: int
    logoType: int
    subscriptInfo: dict[{'albumSubscriptValue': int, 'url': str}]
    albumSubscript: int


class FollowingInfo(TypedDict):
    uid: int
    coverPath: str
    anchorNickName: str
    background: str
    description: str
    url: str
    grade: int
    mvpGrade: int
    gradeType: int
    trackCount: int
    albumCount: int
    followerCount: int
    followingCount: int
    isFollow: bool
    beFollow: bool
    isBlack: bool
    logoType: int


class PubInfo(TypedDict):
    id: int
    title: str
    subTitle: str
    coverPath: str
    isFinished: bool
    isPaid: bool
    anchorUrl: str
    anchorNickname: str
    anchorUid: int
    playCount: int
    trackCount: int
    albumUrl: str
    description: str
    vipType: int
    albumSubscript: int


class SubscriptionInfo(TypedDict):
    id: int
    title: str
    subTitle: str
    description: str
    coverPath: str
    isFinished: bool
    isPaid: bool
    anchor: dict[{'anchorUrl': str, 'anchorNickName': str, 'anchorUid': int, 'anchorCoverPath': str, 'logoType': int}]
    playCount: int
    trackCount: int
    albumUrl: str
    albumStatus: int
    lastUptrackAt: int
    lastUptrackAtStr: str
    serialState: int
    isTop: bool
    categoryCode: str
    categoryTitle: str
    lastUptrackUrl: str
    lastUptrackTitle: str
    vipType: int
    albumSubscript: int
    albumScore: str


class TrackInfo(TypedDict):
    trackId: int
    title: str
    trackUrl: str
    coverPath: str
    createTimeAsString: str
    albumId: int
    albumTitle: str
    albumUrl: str
    anchorUid: int
    anchorUrl: str
    nickname: str
    durationAsString: str
    playCount: int
    showLikeBtn: bool
    isLike: bool
    isPaid: bool
    isRelay: bool
    showDownloadBtn: bool
    showCommentBtn: bool
    showForwardBtn: bool
    isVideo: bool
    videoCover: str
    breakSecond: int
    length: int
    isAlbumShow: bool


class UserBasicInfo(TypedDict):
    uid: int
    nickName: str
    cover: str
    background: str
    isVip: bool
    constellationType: int
    personalSignature: str
    personalDescription: str
    fansCount: int
    gender: int
    birthMonth: int
    birthDay: int
    province: str
    city: str
    anchorGrade: int
    mvpGrade: int
    anchorGradeType: int
    isMusician: bool
    anchorUrl: str
    relation: dict[{'isFollow': bool, 'beFollow': bool, 'isBlack': bool}] | None
    liveInfo: dict[{'id': int, 'roomId': int, 'coverPath': str, 'liveUrl': str, 'status': int}] | None
    logoType: int
    followingCount: int
    tracksCount: int
    albumsCount: int
    albumCountReal: int
    userCompany: str
    qualificationGuideInfos: list[str]


class UserDetailedInfo(TypedDict):
    uid: int
    pubPageInfo: dict[{'totalCount': int, 'pubInfoList': list[PubInfo]}]
    trackPageInfo: dict[{'totalCount': int, 'trackInfoList': list[TrackInfo]}]
    subscriptionPageInfo: dict[{'privateSub': bool, 'totalCount': int, 'subscribeInfoList': list[SubscriptionInfo]}]
    followingPageInfo: dict[{'totalCount': int, 'followInfoList': list[FollowingInfo]}]


class UserTag(TypedDict):
    businessName: str
    businessType: int
    extra: dict
    height: int
    icon: str
    jumpUrl: str
    scale: int
    width: int
