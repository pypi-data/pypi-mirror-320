from typing import Optional, List

from pydantic import BaseModel

from Grindr.client.web.routes.fetch.fetch_profile import Media
from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V3


class ProfileData(BaseModel):
    profileId: str | None = None
    seen: int
    isFavorite: bool | None = None
    displayName: str | None = None
    profileImageMediaHash: str | None = None
    age: str | None = None
    showDistance: bool | None = None
    isNew: bool | None = None
    distance: float | None = None
    lastChatTimestamp: int | None = None
    medias: list[Media] | None = None
    lastUpdatedTime: int | None = None
    lastViewed: int | None = None
    rightNow: str | None = None
    rightNowText: str | None = None
    rightNowPosted: int | None = None
    rightNowDistance: float | None = None
    nsfw: bool | None = None
    acceptNSFWPics: bool | None = None
    verifiedInstagramId: str | None = None
    isBlockable: bool | None = None


class FetchProfilesRouteResponse(BaseModel):
    profiles: list[ProfileData]


class FetchProfilesRoutePayload(BodyParams):
    targetProfileIds: list[str]


class FetchProfilesRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V3, "/profiles"),
        None,
        FetchProfilesRoutePayload,
        FetchProfilesRouteResponse
    ]
):
    """
    Retrieve a session from the API

    """
