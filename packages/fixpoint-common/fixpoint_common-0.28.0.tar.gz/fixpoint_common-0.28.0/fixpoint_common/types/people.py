"""Models for people data."""

__all__ = ["PersonData", "PersonLinkedinProfile", "Education"]


from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from fixpoint_common.types.companies import WorkExperience, Location


class PersonData(BaseModel):
    """Overview data about a person's work experience and education."""

    linkedin_url: str = Field(description="The LinkedIn URL of the person")
    linkedin_profile: "PersonLinkedinProfile" = Field(
        description="The person's LinkedIn profile"
    )
    name: str = Field(description="The name of the person")
    location: Location = Field(description="Where the person lives/works")
    work_experience: List[WorkExperience] = Field(
        description="The person's work experience. To filter to current jobs, check the that each end_date is None"  # pylint: disable=line-too-long
    )
    education: List["Education"] = Field(description="The person's education")


class PersonLinkedinProfile(BaseModel):
    """A person's LinkedIn profile data."""

    url: str = Field(description="The LinkedIn URL of the person")
    updated_at: datetime = Field(
        description="The timestamp when the person updated their Linkedin"
    )
    headline: str = Field(description="The person's headline")
    about_me: str = Field(description="The person's about me summary")
    profile_picture_url: Optional[str] = Field(
        description="The URL of the person's profile picture"
    )


class Education(BaseModel):
    """A person's education data."""

    school: str = Field(description="The name of the school")
    degree_name: str = Field(description="The degree the person has")
    field_of_study: str = Field(description="The field of study the person has")
    start_date: datetime = Field(description="The start date of the person's education")
    end_date: datetime = Field(description="The end date of the person's education")
