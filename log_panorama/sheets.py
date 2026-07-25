from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from log_panorama.models import PLACE_HEADERS, PanoramaLocation, PlaceCode, SHEET_HEADERS, normalize_sheet_records


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class SheetConfigError(RuntimeError):
    """Raised when Google Sheets configuration is missing or invalid."""


class PlaceCodeSheetStore:
    def __init__(self, worksheet: Any):
        self.worksheet = worksheet
        self.ensure_headers()

    def ensure_headers(self) -> None:
        first_row = self.worksheet.row_values(1)
        first_row_clean = [v.strip() for v in first_row]
        if first_row_clean != PLACE_HEADERS:
            end_col = chr(ord("A") + len(PLACE_HEADERS) - 1)
            self.worksheet.update(range_name=f"A1:{end_col}1", values=[PLACE_HEADERS])

    def list_places(self) -> list[PlaceCode]:
        rows = self.worksheet.get_all_records()
        return [
            PlaceCode.from_sheet_row(row)
            for row in rows
            if str(row.get("Mã địa điểm", "")).strip()
        ]

    def upsert(self, place: PlaceCode) -> str:
        row_index = self._find_row_index(place)
        if row_index is None:
            self.worksheet.append_row(place.to_sheet_row(), value_input_option="USER_ENTERED")
            return "created"
        self.worksheet.update(
            range_name=f"A{row_index}:B{row_index}",
            values=[place.to_sheet_row()],
        )
        return "updated"

    def _find_row_index(self, target: PlaceCode) -> int | None:
        for offset, place in enumerate(self.list_places(), start=2):
            if place.key == target.key:
                return offset
        return None


class PanoramaSheetStore:
    def __init__(self, worksheet: Any):
        self.worksheet = worksheet
        self.ensure_headers()

    def ensure_headers(self) -> None:
        first_row = self.worksheet.row_values(1)
        # Strip mỗi cell để tránh lỗi khoảng trắng/BOM khi so sánh
        first_row_clean = [v.strip() for v in first_row]
        if first_row_clean != SHEET_HEADERS:
            end_col = chr(ord("A") + len(SHEET_HEADERS) - 1)
            self.worksheet.update(range_name=f"A1:{end_col}1", values=[SHEET_HEADERS])

    def list_records(self) -> list[PanoramaLocation]:
        rows = self.worksheet.get_all_records()
        return normalize_sheet_records(rows)

    def upsert(self, record: PanoramaLocation) -> str:
        row_index = self._find_row_index(record)
        if row_index is None:
            self.worksheet.append_row(record.to_sheet_row(), value_input_option="USER_ENTERED")
            return "created"

        self.worksheet.update(
            range_name=f"A{row_index}:G{row_index}",
            values=[record.to_sheet_row()],
        )
        return "updated"

    def delete(self, place_code: str, hotspot: str) -> bool:
        target = PanoramaLocation(
            place_code=place_code.strip(),
            place_name="-",
            hotspot=hotspot.strip(),
        )
        row_index = self._find_row_index(target)
        if row_index is None:
            return False

        self.worksheet.delete_rows(row_index)
        return True

    def _find_row_index(self, target: PanoramaLocation) -> int | None:
        for offset, record in enumerate(self.list_records(), start=2):
            if record.key == target.key:
                return offset
        return None


def _connect(secrets: Mapping[str, Any]) -> gspread.Spreadsheet:
    try:
        sheet_id = secrets["sheets"]["spreadsheet_id"]
        service_account_info = dict(secrets["gcp_service_account"])
    except KeyError as exc:
        raise SheetConfigError(
            "Thieu cau hinh Streamlit secrets cho Google Sheets."
        ) from exc

    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES,
    )
    client = gspread.authorize(credentials)
    return client.open_by_key(sheet_id)


def build_stores(secrets: Mapping[str, Any]) -> tuple[PanoramaSheetStore, PlaceCodeSheetStore]:
    spreadsheet = _connect(secrets)

    log_ws_name = secrets["sheets"].get("worksheet_name", "panorama_logs")
    try:
        log_ws = spreadsheet.worksheet(log_ws_name)
    except gspread.WorksheetNotFound:
        log_ws = spreadsheet.add_worksheet(
            title=log_ws_name, rows=1000, cols=len(SHEET_HEADERS),
        )

    place_ws_name = secrets["sheets"].get("place_codes_worksheet_name", "place_codes")
    try:
        place_ws = spreadsheet.worksheet(place_ws_name)
    except gspread.WorksheetNotFound:
        place_ws = spreadsheet.add_worksheet(
            title=place_ws_name, rows=100, cols=len(PLACE_HEADERS),
        )

    return PanoramaSheetStore(log_ws), PlaceCodeSheetStore(place_ws)

