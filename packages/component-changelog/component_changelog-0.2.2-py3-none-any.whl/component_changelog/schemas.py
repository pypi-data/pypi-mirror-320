from __future__ import annotations

from collections.abc import Sequence
from datetime import date, timedelta

from packaging.version import Version
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_serializer, field_validator


class Changes(BaseModel):
    features: list[str] = Field(default_factory=list)
    fixes: list[str] = Field(default_factory=list)
    breaking: list[str] = Field(default_factory=list)
    miscellaneous: list[str] = Field(default_factory=list)

    def merge(self, other: Changes) -> None:
        self.features += other.features
        self.fixes += other.fixes
        self.breaking += other.breaking
        self.miscellaneous += other.miscellaneous


class VersionChanges(BaseModel):
    version: Version
    created_at: date
    changes: dict[str, Changes] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("version", mode="before")
    def validate_version(cls, value: str | Version) -> Version:
        if isinstance(value, str):
            value = Version(value)
        return value

    @field_serializer("version", when_used="always")
    def serialize_version(self, value: Version) -> str:
        return str(value)

    @property
    def week_of(self) -> date:
        return self.created_at - timedelta(days=self.created_at.weekday())


class ComponentChangelog(BaseModel):
    component: str
    versions: Sequence[VersionChanges] = Field(default_factory=list)

    def filtered(self, upto_version: str) -> Sequence[VersionChanges]:
        max_version = Version(upto_version)
        entries = [entry for entry in self.versions if entry.version <= max_version]
        return entries


class WeeklyChangelog(BaseModel):
    week_of: date
    changes: dict[str, Changes] = Field(default_factory=dict)


ApplicationChangelog = RootModel[Sequence[WeeklyChangelog]]
