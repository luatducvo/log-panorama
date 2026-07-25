from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


SHEET_HEADERS = [
    "place_code",
    "place_name",
    "hotspot",
    "connects_to",
    "updated_at",
]


class ValidationError(ValueError):
    """Raised when a panorama location record is invalid."""


@dataclass(frozen=True)
class PanoramaLocation:
    place_code: str
    place_name: str
    hotspot: str
    connects_to: str = ""
    updated_at: str = ""

    @classmethod
    def from_form(
        cls,
        place_code: str,
        place_name: str,
        hotspot: str,
        connects_to: str = "",
    ) -> "PanoramaLocation":
        record = cls(
            place_code=place_code.strip(),
            place_name=place_name.strip(),
            hotspot=hotspot.strip(),
            connects_to=connects_to.strip(),
            updated_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        record.validate()
        return record

    @classmethod
    def from_sheet_row(cls, row: dict[str, object]) -> "PanoramaLocation":
        return cls(
            place_code=str(row.get("place_code", "")).strip(),
            place_name=str(row.get("place_name", "")).strip(),
            hotspot=str(row.get("hotspot", "")).strip(),
            connects_to=str(row.get("connects_to", "")).strip(),
            updated_at=str(row.get("updated_at", "")).strip(),
        )

    @property
    def key(self) -> tuple[str, str]:
        return (self.place_code.casefold(), self.hotspot.casefold())

    def validate(self) -> None:
        missing = []
        if not self.place_code:
            missing.append("ma dia diem")
        if not self.place_name:
            missing.append("ten dia diem")
        if not self.hotspot:
            missing.append("hotspot cua dia diem")

        if missing:
            raise ValidationError("Vui long nhap: " + ", ".join(missing))

    def to_sheet_row(self) -> list[str]:
        return [
            self.place_code,
            self.place_name,
            self.hotspot,
            self.connects_to,
            self.updated_at,
        ]


def normalize_sheet_records(rows: list[dict[str, object]]) -> list[PanoramaLocation]:
    records = [PanoramaLocation.from_sheet_row(row) for row in rows]
    return [record for record in records if record.place_code or record.hotspot]

