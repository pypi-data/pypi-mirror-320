from typing import TypedDict


class WebChannel(TypedDict, total=False):
    id: int
    name: str
    country: dict | None
    officialSite: str


class Image(TypedDict, total=False):
    medium: str
    original: str


class Show(TypedDict, total=False):
    id: int
    name: str
    premiered: str | None
    network: dict | None
    webChannel: WebChannel | None
    image: Image | None
    summary: str | None


class Season(TypedDict, total=False):
    id: int
    url: str
    number: int
    name: str
    episodeOrder: int
    premiereDate: str | None
    endDate: str | None
    network: dict | None
    webChannel: WebChannel | None
    image: Image | None
    summary: str | None
    _links: dict
