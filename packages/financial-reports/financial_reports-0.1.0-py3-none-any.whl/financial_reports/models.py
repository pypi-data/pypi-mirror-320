from typing import Any, TypedDict, Union, Optional


class Filing(TypedDict):
    id: int
    company: dict[str, Any]
    filing_type: dict[str, str]
    language: dict[str, str]
    title: str
    added_to_platform: str
    updated_date: str
    dissemination_datetime: str
    release_datetime: str
    source: dict[str, str]
    document: str


class Sector(TypedDict):
    code: str
    name: str


class IndustryGroup(TypedDict):
    code: str
    name: str
    sector: Sector


class Industry(TypedDict):
    code: str
    name: str
    industry_group: IndustryGroup


class SubIndustry(TypedDict):
    code: str
    name: str
    industry: Industry


class Company(TypedDict):
    id: int
    name: str
    isins: list[str]
    lei: str
    country: str
    sector: Sector
    industry_group: IndustryGroup
    industry: Industry
    sub_industry: SubIndustry
    ir_link: str
    homepage_link: str
    date_public: str
    date_ipo: str
    main_stock_exchange: str
    social_facebook: Optional[str]
    social_instagram: Optional[str]
    social_twitter: Optional[str]
    social_linkedin: Optional[str]
    social_youtube: Optional[str]
    social_tiktok: Optional[str]
    social_pinterest: Optional[str]
    social_xing: Optional[str]
    social_glassdoor: Optional[str]
    year_founded: str
    corporate_video_id: Optional[str]
    served_area: str
    headcount: int
    contact_email: str
    ticker: str
    is_listed: bool


class FilingResponse(TypedDict):
    count: int
    next: Union[str, None]
    previous: Union[str, None]
    results: list[Filing]


class CompanyResponse(TypedDict):
    count: int
    next: Union[str, None]
    previous: Union[str, None]
    results: list[Company]


class FilingTypeResponse(TypedDict):
    count: int
    next: Union[str, None]
    previous: Union[str, None]
    results: list[dict[str, str]]


class SourceResponse(TypedDict):
    count: int
    next: Union[str, None]
    previous: Union[str, None]
    results: list[dict[str, str]]


class SectorResponse(TypedDict):
    count: int
    next: Union[str, None]
    previous: Union[str, None]
    results: list[dict[str, str]]


class IndustryResponse(TypedDict):
    count: int
    next: Union[str, None]
    previous: Union[str, None]
    results: list[dict[str, Any]]
