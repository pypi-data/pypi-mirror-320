import time
from uuid import uuid4
from datetime import datetime
from typing import List, Optional, Any, Dict
from .utils import generate_android_device_id, generate_uuid, generate_user_agent
from pydantic import BaseModel, FilePath, HttpUrl, ValidationError, validator


def validate_external_url(cls, v : str):
    if v is None or (v.startswith("http") and "://" in v) or isinstance(v, str):
        return v
    raise ValidationError("external_url must been URL or string")

class AuthorizationData(BaseModel):
    ds_user_id: Optional[str]
    sessionid: Optional[str]
    should_use_header_over_cookies : bool = True

class DeviceSettings(BaseModel, frozen=True):
    app_version: str = "313.0.0.0.60"
    android_version: int = 29
    android_release: str = "10.0.0"
    dpi: str = "420dpi"
    resolution: str = "1080x2104"
    manufacturer: str = "samsung"
    device: str = "xcoverpro"
    model: str = "SM-G715U"
    cpu: str = "exynos9611"
    version_code: str = "547897021"


class AccountUUIDs(BaseModel, frozen=True):
    phone_id: str = generate_uuid()
    uuid: str = generate_uuid()
    client_session_id: str = generate_uuid()
    advertising_id: str = generate_uuid()
    comment_session_id : str = generate_uuid()
    request_id: str = generate_uuid()
    tray_session_id: str = generate_uuid()
    android_device_id: str = generate_android_device_id()

class Credentials(BaseModel):
    uuids : AccountUUIDs = AccountUUIDs() 
    ig_u_rur: Optional[str] = None
    ig_www_claim: Optional[str] = None
    mid: Optional[str] = None
    shbts: Optional[str] = None
    shbid: Optional[str] = None
    region_hint: Optional[str] = None
    authorization_data: Optional[AuthorizationData] = None
    cookies: Dict[str, Any] = {}
    last_login: float = time.time()
    device_settings: DeviceSettings = DeviceSettings()
    country: str = 'US'
    country_code: int = 1
    locale: str = 'en_US'
    user_agent: str = generate_user_agent(dict(device_settings.dict(), locale=locale))
    timezone_offset: int = -21600

class Resource(BaseModel, frozen=True):
    pk: str
    video_url: Optional[HttpUrl]  # for Video and IGTV
    thumbnail_url: HttpUrl
    media_type: int


class User(BaseModel, frozen=True):
    pk: str
    username: str
    full_name: str
    is_private: bool
    profile_pic_url: HttpUrl
    profile_pic_url_hd: Optional[HttpUrl]
    is_verified: bool
    media_count: int
    follower_count: int
    following_count: int
    biography: Optional[str] = ""
    external_url: Optional[str]
    account_type: Optional[int]
    is_business: bool

    public_email: Optional[str]
    contact_phone_number: Optional[str]
    public_phone_country_code: Optional[str]
    public_phone_number: Optional[str]
    business_contact_method: Optional[str]
    business_category_name: Optional[str]
    category_name: Optional[str]
    category: Optional[str]

    address_street: Optional[str]
    city_id: Optional[str]
    city_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    zip: Optional[str]
    instagram_location_id: Optional[str]
    interop_messaging_user_fbid: Optional[str]

    _external_url = validator("external_url", allow_reuse=True)(validate_external_url)


class Account(BaseModel, frozen=True):
    pk: str
    username: str
    full_name: str
    is_private: bool
    profile_pic_url: HttpUrl
    is_verified: bool
    biography: Optional[str] = ""
    external_url: Optional[str]
    is_business: bool
    birthday: Optional[str]
    phone_number: Optional[str]
    gender: Optional[int]
    email: Optional[str]

    _external_url = validator("external_url", allow_reuse=True)(validate_external_url)


class UserShort(BaseModel, frozen=True):
    pk: str
    username: Optional[str]
    full_name: Optional[str] = ""
    profile_pic_url: Optional[HttpUrl]
    profile_pic_url_hd: Optional[HttpUrl]
    is_private: Optional[bool]
    # is_verified: bool  # not found in hashtag_medias_v1
    stories: List = []
    latest_reel_media : Optional[int]= None
    

class Usertag(BaseModel, frozen=True):
    user: UserShort
    x: float
    y: float


class Location(BaseModel, frozen=True):
    pk: Optional[int]
    name: str
    phone: Optional[str] = ""
    website: Optional[str] = ""
    category: Optional[str] = ""
    hours: Optional[dict] = {}  # opening hours
    address: Optional[str] = ""
    city: Optional[str] = ""
    zip: Optional[str] = ""
    lng: Optional[float]
    lat: Optional[float]
    external_id: Optional[int]
    external_id_source: Optional[str]
    # address_json: Optional[dict] = {}
    # profile_pic_url: Optional[HttpUrl]
    # directory: Optional[dict] = {}


class Media(BaseModel, frozen=True):
    pk: str
    id: str
    code: str
    taken_at: datetime
    media_type: int
    image_versions2: Optional[dict] = {}
    product_type: Optional[str] = ""  # igtv or feed
    thumbnail_url: Optional[HttpUrl]
    location: Optional[Location] = None
    user: UserShort
    comment_count: Optional[int] = 0
    comments_disabled: Optional[bool] = False
    commenting_disabled_for_viewer: Optional[bool] = False
    like_count: int
    play_count: Optional[int]
    has_liked: Optional[bool]
    caption_text: str
    accessibility_caption: Optional[str]
    usertags: List[Usertag]
    sponsor_tags: List[UserShort]
    video_url: Optional[HttpUrl]  # for Video and IGTV
    view_count: Optional[int] = 0  # for Video and IGTV
    video_duration: Optional[float] = 0.0  # for Video and IGTV
    title: Optional[str] = ""
    resources: List[Resource] = []
    clips_metadata: dict = {}


class MediaXma(BaseModel, frozen=True):
    # media_type: int
    video_url: Optional[HttpUrl]  # for Video and IGTV
    title: Optional[str] = ""
    preview_url: Optional[HttpUrl]
    preview_url_mime_type: Optional[str]
    header_icon_url: Optional[HttpUrl]
    header_icon_width: Optional[int]
    header_icon_height: Optional[int]
    header_title_text: Optional[str]
    preview_media_fbid: Optional[str]


class MediaOembed(BaseModel, frozen=True):
    title: str
    author_name: str
    author_url: str
    author_id: str
    media_id: str
    provider_name: str
    provider_url: HttpUrl
    type: str
    width: Optional[int] = None
    height: Optional[int] = None
    html: str
    thumbnail_url: HttpUrl
    thumbnail_width: int
    thumbnail_height: int
    can_view: bool


class Collection(BaseModel, frozen=True):
    id: str
    name: str
    type: str
    media_count: int


class Comment(BaseModel, frozen=True):
    pk: str
    text: str
    user: UserShort
    created_at_utc: datetime
    content_type: str
    status: str
    has_liked: Optional[bool]
    like_count: Optional[int]


class Hashtag(BaseModel, frozen=True):
    id: str
    name: str
    media_count: Optional[int]
    profile_pic_url: Optional[HttpUrl]


class StoryMention(BaseModel, frozen=True):
    user: UserShort
    x: Optional[float]
    y: Optional[float]
    width: Optional[float]
    height: Optional[float]


class StoryMedia(BaseModel, frozen=True):
    # Instagram does not return the feed_media object when requesting story,
    # so you will have to make an additional request to get media and this is overhead:
    # media: Media
    x: float = 0.5
    y: float = 0.4997396
    z: float = 0
    width: float = 0.8
    height: float = 0.60572916
    rotation: float = 0.0
    is_pinned: Optional[bool]
    is_hidden: Optional[bool]
    is_sticker: Optional[bool]
    is_fb_sticker: Optional[bool]
    media_pk: int
    user_id: Optional[int]
    product_type: Optional[str]
    media_code: Optional[str]


class StoryHashtag(BaseModel, frozen=True):
    hashtag: Hashtag
    x: Optional[float]
    y: Optional[float]
    width: Optional[float]
    height: Optional[float]


class StoryLocation(BaseModel, frozen=True):
    location: Location
    x: Optional[float]
    y: Optional[float]
    width: Optional[float]
    height: Optional[float]


class StoryStickerLink(BaseModel, frozen=True):
    url: HttpUrl
    link_title: Optional[str]
    link_type: Optional[str]
    display_url: Optional[str]


class StorySticker(BaseModel, frozen=True):
    id: Optional[str]
    type: Optional[str] = "gif"
    x: float
    y: float
    z: Optional[int] = 1000005
    width: float
    height: float
    rotation: Optional[float] = 0.0
    story_link: Optional[StoryStickerLink]
    extra: Optional[dict] = {}


class StoryBuild(BaseModel, frozen=True):
    mentions: List[StoryMention]
    path: FilePath
    paths: List[FilePath] = []
    stickers: List[StorySticker] = []


class StoryLink(BaseModel, frozen=True):
    webUri: HttpUrl
    x: float = 0.5126011
    y: float = 0.5168225
    z: float = 0.0
    width: float = 0.50998676
    height: float = 0.25875
    rotation: float = 0.0


class Story(BaseModel, frozen=True):
    pk: str
    id: str
    code: str
    taken_at: datetime
    media_type: int
    product_type: Optional[str] = ""
    thumbnail_url: Optional[HttpUrl]
    user: UserShort
    video_url: Optional[HttpUrl]  # for Video and IGTV
    video_duration: Optional[float] = 0.0  # for Video and IGTV
    sponsor_tags: List[UserShort]
    mentions: List[StoryMention]
    links: List[StoryLink]
    hashtags: List[StoryHashtag]
    locations: List[StoryLocation]
    stickers: List[StorySticker]
    medias: List[StoryMedia] = []


class Guide(BaseModel, frozen=True):
    id: Optional[str]
    title: Optional[str]
    description: str
    cover_media: Media
    feedback_item: Optional[dict]


class DirectMedia(BaseModel, frozen=True):
    id: str
    media_type: int
    user: Optional[UserShort]
    thumbnail_url: Optional[HttpUrl]
    video_url: Optional[HttpUrl]
    audio_url: Optional[HttpUrl]


class ReplyMessage(BaseModel, frozen=True):
    id: str
    user_id: Optional[str]
    timestamp: datetime
    item_type: Optional[str]
    is_sent_by_viewer: Optional[bool]
    is_shh_mode: Optional[bool]
    text: Optional[str]
    link: Optional[dict]
    animated_media: Optional[dict]
    media: Optional[DirectMedia]
    visual_media: Optional[dict]
    media_share: Optional[Media]
    reel_share: Optional[dict]
    story_share: Optional[dict]
    felix_share: Optional[dict]
    xma_share: Optional[MediaXma]
    clip: Optional[Media]
    placeholder: Optional[dict]


class DirectMessage(BaseModel, frozen=True):
    id: str  # e.g. 28597946203914980615241927545176064
    user_id: Optional[str]
    thread_id: Optional[int]  # e.g. 340282366841710300949128531777654287254
    timestamp: datetime
    item_type: Optional[str]
    is_sent_by_viewer: Optional[bool]
    is_shh_mode: Optional[bool]
    reactions: Optional[dict]
    text: Optional[str]
    reply: Optional[ReplyMessage]
    link: Optional[dict]
    animated_media: Optional[dict]
    media: Optional[DirectMedia]
    visual_media: Optional[dict]
    media_share: Optional[Media]
    reel_share: Optional[dict]
    story_share: Optional[dict]
    felix_share: Optional[dict]
    xma_share: Optional[MediaXma]
    clip: Optional[Media]
    placeholder: Optional[dict]


class DirectResponse(BaseModel, frozen=True):
    unseen_count: Optional[int]
    unseen_count_ts: Optional[int]
    status: Optional[str]


class DirectShortThread(BaseModel, frozen=True):
    id: str
    users: List[UserShort]
    named: bool
    thread_title: str
    pending: bool
    thread_type: str
    viewer_id: str
    is_group: bool


class DirectThread(BaseModel, frozen=True):
    pk: str  # thread_v2_id, e.g. 17898572618026348
    id: str  # thread_id, e.g. 340282366841510300949128268610842297468
    messages: List[DirectMessage]
    users: List[UserShort]
    inviter: Optional[UserShort]
    left_users: List[UserShort] = []
    admin_user_ids: list
    last_activity_at: datetime
    muted: bool
    is_pin: Optional[bool]
    named: bool
    canonical: bool
    pending: bool
    archived: bool
    thread_type: str
    thread_title: str
    folder: int
    vc_muted: bool
    is_group: bool
    mentions_muted: bool
    approval_required_for_new_members: bool
    input_mode: int
    business_thread_folder: int
    read_state: int
    is_close_friend_thread: bool
    assigned_admin_id: int
    shh_mode_enabled: bool
    last_seen_at: Optional[dict] = {}

    def is_seen(self, user_id: str):
        """Have I seen this thread?
        :param user_id: You account user_id
        """
        user_id = str(user_id)
        own_timestamp = int(self.last_seen_at[user_id]["timestamp"])
        timestamps = [
            (int(v["timestamp"]) - own_timestamp) > 0
            for k, v in self.last_seen_at.items()
            if k != user_id
        ]
        return not any(timestamps)


class Relationship(BaseModel, frozen=True):
    user_id: str
    blocking: bool
    followed_by: bool
    following: bool
    incoming_request: bool
    is_bestie: bool
    is_blocking_reel: bool
    is_muting_reel: bool
    is_private: bool
    is_restricted: bool
    muting: bool
    outgoing_request: bool


class RelationshipShort(BaseModel, frozen=True):
    user_id: str
    following: bool
    incoming_request: bool
    is_bestie: bool
    is_feed_favorite: bool
    is_private: bool
    is_restricted: bool
    outgoing_request: bool


class Highlight(BaseModel, frozen=True):
    pk: str  # 17895485401104052
    id: str  # highlight:17895485401104052
    latest_reel_media: int
    cover_media: dict
    user: UserShort
    title: str
    created_at: datetime
    is_pinned_highlight: bool
    media_count: int
    media_ids: List[int] = []
    items: List[Story] = []


class Share(BaseModel, frozen=True):
    pk: str
    type: str


class Track(BaseModel, frozen=True):
    id: str
    title: str
    subtitle: str
    display_artist: str
    audio_cluster_id: int
    artist_id: Optional[int]
    cover_artwork_uri: Optional[HttpUrl]
    cover_artwork_thumbnail_uri: Optional[HttpUrl]
    progressive_download_url: Optional[HttpUrl]
    fast_start_progressive_download_url: Optional[HttpUrl]
    reactive_audio_download_url: Optional[HttpUrl]
    highlight_start_times_in_ms: List[int]
    is_explicit: bool
    dash_manifest: str
    uri: Optional[HttpUrl]
    has_lyrics: bool
    audio_asset_id: int
    duration_in_ms: int
    dark_message: Optional[str]
    allows_saving: bool
    territory_validity_periods: dict


class Note(BaseModel, frozen=True):
    id: str
    text: str
    user_id: str
    user: UserShort
    audience: int
    created_at: datetime
    expires_at: datetime
    is_emoji_only: bool
    has_translation: bool
    note_style: int
