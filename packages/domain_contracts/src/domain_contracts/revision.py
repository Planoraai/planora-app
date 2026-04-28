"""Validator feedback contract."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RevisionRequest(BaseModel):
    approved: bool = False
    issues: list[str] = Field(default_factory=list)
    requested_changes: list[str] = Field(default_factory=list)
