from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


PLACE_HEADERS = [
    "Mã địa điểm",
    "Mô tả địa điểm",
]


@dataclass(frozen=True)
class PlaceCode:
    code: str
    name: str = ""

    @classmethod
    def from_sheet_row(cls, row: dict[str, object]) -> "PlaceCode":
        return cls(
            code=str(row.get("Mã địa điểm", "")).strip(),
            name=str(row.get("Mô tả địa điểm", "")).strip(),
        )

    def to_sheet_row(self) -> list[str]:
        return [self.code, self.name]

    @property
    def key(self) -> str:
        return self.code.casefold()


MEMBER_HEADERS = [
    "Mã thành viên",
    "Tên thành viên",
]


@dataclass(frozen=True)
class Member:
    code: str
    name: str = ""

    @classmethod
    def from_sheet_row(cls, row: dict[str, object]) -> "Member":
        return cls(
            code=str(row.get("Mã thành viên", "")).strip(),
            name=str(row.get("Tên thành viên", "")).strip(),
        )

    def to_sheet_row(self) -> list[str]:
        return [self.code, self.name]

    @property
    def key(self) -> str:
        return self.code.casefold()


SHEET_HEADERS = [
    "Mã địa điểm",
    "Mô tả địa điểm",
    "Hotspot",
    "Hotspot nối",
    "Thành viên",
    "Vĩ độ",
    "Kinh độ",
    "Cập nhật",
]


class ValidationError(ValueError):
    """Raised when a panorama location record is invalid."""


@dataclass(frozen=True)
class PanoramaLocation:
    place_code: str
    place_name: str
    hotspot: str
    connects_to: str = ""
    member: str = ""
    latitude: str = ""
    longitude: str = ""
    updated_at: str = ""

    @classmethod
    def from_form(
        cls,
        place_code: str,
        place_name: str,
        hotspot: str,
        connects_to: str = "",
        member: str = "",
        latitude: str = "",
        longitude: str = "",
    ) -> "PanoramaLocation":
        record = cls(
            place_code=place_code.strip(),
            place_name=place_name.strip(),
            hotspot=hotspot.strip(),
            connects_to=connects_to.strip(),
            member=member.strip(),
            latitude=latitude.strip(),
            longitude=longitude.strip(),
            updated_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        record.validate()
        return record

    @classmethod
    def from_sheet_row(cls, row: dict[str, object]) -> "PanoramaLocation":
        return cls(
            place_code=str(row.get("Mã địa điểm", "")).strip(),
            place_name=str(row.get("Mô tả địa điểm", "")).strip(),
            hotspot=str(row.get("Hotspot", "")).strip(),
            connects_to=str(row.get("Hotspot nối", "")).strip(),
            member=str(row.get("Thành viên", "")).strip(),
            latitude=str(row.get("Vĩ độ", "")).strip(),
            longitude=str(row.get("Kinh độ", "")).strip(),
            updated_at=str(row.get("Cập nhật", "")).strip(),
        )

    @property
    def key(self) -> tuple[str, str]:
        return (self.place_code.casefold(), self.hotspot.casefold())

    def validate(self) -> None:
        missing = []
        if not self.place_code:
            missing.append("mã địa điểm")
        if not self.place_name:
            missing.append("mô tả địa điểm")
        if not self.hotspot:
            missing.append("hotspot của địa điểm")

        for label, val in [("vĩ độ (latitude)", self.latitude), ("kinh độ (longitude)", self.longitude)]:
            if val:
                try:
                    float(val)
                except ValueError:
                    missing.append(f"{label} phải là số thực")

        if missing:
            raise ValidationError("Vui lòng nhập đúng: " + ", ".join(missing))

    def to_sheet_row(self) -> list[str]:
        return [
            self.place_code,
            self.place_name,
            self.hotspot,
            self.connects_to,
            self.member,
            self.latitude,
            self.longitude,
            self.updated_at,
        ]


def normalize_sheet_records(rows: list[dict[str, object]]) -> list[PanoramaLocation]:
    records = [PanoramaLocation.from_sheet_row(row) for row in rows]
    return [record for record in records if record.place_code or record.hotspot]


def make_abbreviation(name: str) -> str:
    """Chuyển 'Quảng trường Đại Đoàn Kết' → 'QTĐĐK'"""
    return "".join(word[0].upper() for word in name.split() if word)


def suggest_next_hotspot_number(records: list[PanoramaLocation], abbreviation: str, zone: str) -> str:
    """Đề xuất số thứ tự tiếp theo cho hotspot dạng {abbreviation}-{zone}-NNN."""
    prefix = f"{abbreviation}-{zone}-"
    max_num = 0
    for r in records:
        if r.hotspot.casefold().startswith(prefix.casefold()):
            suffix = r.hotspot[len(prefix):]
            if suffix.isdigit() and len(suffix) == 3:
                max_num = max(max_num, int(suffix))
    return f"{max_num + 1:03d}"

