"""
Pydantic Models for CompasScan API

This module centralizes all data models for type safety and validation.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

# --- Core Business Models ---


class BrandContext(BaseModel):
    """Context information about the target brand."""

    name: str = Field(..., description="Brand name (e.g., 'Hulu')", min_length=1)
    url: str = Field(..., description="Official brand website URL")
    keywords: list[str] = Field(default_factory=list, description="Extracted keywords from brand's website")
    country: Optional[str] = Field(None, description="Detected country from TLD (e.g., 'Chile' from .cl)")
    tld: Optional[str] = Field(None, description="Detected TLD (e.g., 'cl' from bendita.cl)")
    industry_description: Optional[str] = Field(None, description="Title and meta description from the website")
    search_queries: list[str] = Field(default_factory=list, description="Generated search queries used to find competitors")

    model_config = {"from_attributes": True}


class CompetitorCandidate(BaseModel):
    """Raw competitor candidate from search or AI sources."""

    link: str = Field(..., description="Original URL from source")
    clean_url: str = Field(..., description="Cleaned/normalized URL")
    title: Optional[str] = Field(None, description="Page title or competitor name")
    snippet: Optional[str] = Field(None, description="Description or snippet text")
    source: Literal["search", "direct_search", "gemini_knowledge"] = Field(..., description="Source of the candidate")
    gemini_type: Optional[Literal["HDA", "LDA"]] = Field(None, description="Type suggested by Gemini (if from AI)")

    model_config = {"from_attributes": True}


class ClassificationResult(BaseModel):
    """Result of competitor classification."""

    valid: bool = Field(..., description="Whether the candidate is a valid competitor")
    type: Optional[Literal["HDA", "LDA"]] = Field(
        None, description="Competitor type if valid (High/Low Domain Authority)"
    )
    reason: Optional[str] = Field(None, description="Reason for rejection if invalid")
    justification: Optional[str] = Field(None, description="Justification for classification if valid")

    model_config = {"from_attributes": True}


class Competitor(BaseModel):
    """Final validated competitor entry."""

    name: str = Field(..., description="Competitor name or domain", min_length=1)
    url: str = Field(..., description="Official competitor website URL")
    justification: str = Field(..., description="Why this is considered a competitor")

    model_config = {"from_attributes": True}


class DiscardedCandidate(BaseModel):
    """Candidate that was rejected during classification."""

    url: str = Field(..., description="URL of the discarded candidate")
    reason: str = Field(..., description="Reason for rejection")

    model_config = {"from_attributes": True}


class ScanReport(BaseModel):
    """Complete scan report with all competitors and discarded candidates."""

    HDA_Competitors: list[Competitor] = Field(
        default_factory=list, description="High Domain Authority competitors (major players)"
    )
    LDA_Competitors: list[Competitor] = Field(
        default_factory=list, description="Low Domain Authority competitors (niche/emerging)"
    )
    Discarded_Candidates: list[DiscardedCandidate] = Field(
        default_factory=list, description="Candidates that were filtered out with reasons"
    )

    model_config = {"from_attributes": True}


# --- API Models ---


class ScanResponse(BaseModel):
    """Response model for scan endpoint."""

    status: str = Field(..., description="Status of the operation (success/error)")
    target: Optional[str] = Field(None, description="Brand target of the scan")
    data: Optional[ScanReport] = Field(None, description="Competitor scan report")
    message: str = Field(..., description="Descriptive message about the result")
    warnings: Optional[list[str]] = Field(None, description="Non-critical warnings during the process")
    debug: Optional[str] = Field(None, description="Debug information (only in development)")
    brand_context: Optional[BrandContext] = Field(None, description="Search context including keywords and geo-targeting")


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Deployment environment")
    observability: Optional[dict] = Field(None, description="Observability tools status")


# --- Gemini AI Models ---


class GeminiCompetitor(BaseModel):
    """Expected structure from Gemini AI response."""

    name: str = Field(..., description="Competitor name")
    url: str = Field(..., description="Competitor URL")
    type: Literal["HDA", "LDA"] = Field(..., description="Competitor classification")
    description: str = Field(..., description="Justification for classification")

    @field_validator("url")
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        """Ensure URL has proper format."""
        if not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v

    def to_candidate(self) -> CompetitorCandidate:
        """Convert Gemini competitor to CompetitorCandidate."""
        return CompetitorCandidate(
            link=self.url,
            clean_url=self.url,
            title=self.name,  # Use just the name, not "Official Site"
            snippet=self.description,
            source="gemini_knowledge",
            gemini_type=self.type,
        )
