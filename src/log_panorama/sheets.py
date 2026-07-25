from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from log_panorama.models import PanoramaLocation, SHEET_HEADERS, normalize_sheet_records


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class SheetConfigError(RuntimeError):
    """Raised when Google Sheets configuration is missing or invalid."""


class PanoramaSheetStore:
    def __init__(self, worksheet: Any):
        self.worksheet = worksheet
        self.ensure_headers()

    def ensure_headers(self) -> None:
        first_row = self.worksheet.row_values(1)
        if first_row != SHEET_HEADERS:
            self.worksheet.update("A1:E1", [SHEET_HEADERS])

    def list_records(self) -> list[PanoramaLocation]:
        rows = self.worksheet.get_all_records()
        return normalize_sheet_records(rows)

    def upsert(self, record: PanoramaLocation) -> str:
        row_index = self._find_row_index(record)
        if row_index is None:
            self.worksheet.append_row(record.to_sheet_row(), value_input_option="USER_ENTERED")
            return "created"

        self.worksheet.update(f"A{row_index}:E{row_index}", [record.to_sheet_row()])
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


def build_store_from_secrets(secrets: Mapping[str, Any]) -> PanoramaSheetStore:
    try:
        sheet_id = secrets["sheets"]["spreadsheet_id"]
        worksheet_name = secrets["sheets"].get("worksheet_name", "panorama_logs")
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
    spreadsheet = client.open_by_key(sheet_id)

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=len(SHEET_HEADERS))

    return PanoramaSheetStore(worksheet)

