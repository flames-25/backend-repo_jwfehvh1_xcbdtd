"""
Database Schemas for the Portfolio app

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- Portfolio -> "portfolio" collection (singleton with slug="main")
- ProjectItem -> "projectitem" collection (optional if you want per-doc projects)
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectMedia(BaseModel):
    type: str = Field(..., description="image | video | link")
    url: str = Field(..., description="Media URL")
    caption: Optional[str] = Field(None, description="Short caption")


class ProjectItem(BaseModel):
    title: str = Field(..., description="Project title")
    subtitle: Optional[str] = Field(None, description="Short supporting line")
    description: Optional[str] = Field(None, description="Detailed description")
    cover: Optional[str] = Field(None, description="Cover image URL")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering")
    media: List[ProjectMedia] = Field(default_factory=list, description="Additional media items")
    link: Optional[str] = Field(None, description="External link or experience URL")


class SocialLink(BaseModel):
    platform: str = Field(..., description="e.g., twitter, github, discord")
    url: str = Field(..., description="Profile or invite URL")


class Portfolio(BaseModel):
    slug: str = Field("main", description="Singleton identifier")
    username: str = Field(..., description="Display name")
    role: str = Field("Roblox UI/UX Designer", description="Headline role")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(
        None,
        description="Short bio/ elevator pitch",
    )
    accent: str = Field("#00FFE0", description="Accent color (hex)")
    monochrome: bool = Field(True, description="Keep UI black/white with accent")
    socials: List[SocialLink] = Field(default_factory=list, description="Social links")
    projects: List[ProjectItem] = Field(default_factory=list, description="Portfolio items")
