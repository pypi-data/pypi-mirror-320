"""
Models for company data API.
"""

__all__ = [
    "CompanyData",
    "Location",
    "CompanyStats",
    "Competitor",
    "ManagementTeamMember",
    "FundingRound",
    "ManagementTeamMember",
    "NewsArticle",
    "Product",
    "WorkExperience",
]

from typing import List, Optional, TypedDict

from pydantic import BaseModel, Field


class ManagementTeamMember(BaseModel):
    """Information about a management team member."""

    name: str = Field(description="The name of the management team member.")
    title: str = Field(
        description="The title or position of the management team member."
    )
    linkedin_url: Optional[str] = Field(
        description="The LinkedIn URL of the management team member."
    )
    background: Optional[str] = Field(
        description="A summary of the management team member's background."
    )
    board_memberships: List["WorkExperience"] = Field(
        description="The board memberships of the management team member."
    )
    work_experiences: List["WorkExperience"] = Field(
        description="The current and past work experiences of the management team member."
    )


class WorkExperience(BaseModel):
    """A person's work experience.

    If the end_date is None, the person is currently working at the company."""

    company: str
    company_domain: Optional[str]
    role: str
    start_date: Optional[str]
    end_date: Optional[str]
    linkedin_data: Optional["WorkExperienceLinkedIn"] = Field(
        description="The LinkedIn data for the work experience"
    )


class WorkExperienceLinkedIn(BaseModel):
    """A person's work experience data LinkedIn."""

    location: "Location" = Field(description="Where the person's job location was/is")
    employee_description: str
    company_description: Optional[str]


class Product(TypedDict):
    """
    A product of a company.
    """

    name: str
    description: str


class Location(TypedDict):
    """
    A location of a person or company.
    """

    city: Optional[str]
    region: Optional[str]
    country: Optional[str]


class Competitor(TypedDict):
    """
    A competitor of a company.
    """

    name: str
    domain: Optional[str]
    description: Optional[str]
    categories: List[str]
    location: Location
    employee_count_range: Optional[str]


class CompanyStats(TypedDict):
    """
    General statistics about a company.
    """

    employee_count_range: Optional[str]
    employee_count: Optional[int]
    founded_year: Optional[int]
    headquarters: Location
    total_funding_usd: Optional[float]


class FundingRound(TypedDict):
    """
    Information about a funding round.
    """

    name: str
    date: Optional[str]  # ISO format date string
    amount_raised_usd: Optional[float]
    num_investors: Optional[int]
    lead_investors: List[str]


class NewsArticle(TypedDict):
    """
    Information about a news article.
    """

    source: Optional[str]
    date: Optional[str]  # ISO format date string
    title: str
    url: Optional[str]


class CompanyData(BaseModel):
    """Information about a company."""

    company_name: str = Field(description="The name of the company.")
    company_domain: str = Field(description="The domain of the company.")
    management_team: List[ManagementTeamMember] = Field(
        description="The management team of the company."
    )
    description: Optional[str]
    products: List[Product]
    competitors: List[Competitor]
    company_stats: CompanyStats
    funding_rounds: List[FundingRound]
    news: List[NewsArticle]
