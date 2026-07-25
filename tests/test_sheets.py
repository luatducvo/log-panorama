from log_panorama.models import PanoramaLocation, SHEET_HEADERS
from log_panorama.sheets import PanoramaSheetStore


class FakeWorksheet:
    def __init__(self, rows=None, headers=None):
        self.headers = headers or SHEET_HEADERS
        self.rows = rows or []
        self.updated_ranges = []

    def row_values(self, row_index):
        return self.headers if row_index == 1 else []

    def update(self, range_name, values):
        self.updated_ranges.append((range_name, values))
        if range_name == "A1:E1":
            self.headers = values[0]
            return

        row_number = int(range_name.split(":")[0][1:])
        self.rows[row_number - 2] = dict(zip(SHEET_HEADERS, values[0], strict=True))

    def get_all_records(self):
        return self.rows

    def append_row(self, values, value_input_option=None):
        self.rows.append(dict(zip(SHEET_HEADERS, values, strict=True)))

    def delete_rows(self, row_index):
        del self.rows[row_index - 2]


def test_store_repairs_missing_headers():
    worksheet = FakeWorksheet(headers=[])
    PanoramaSheetStore(worksheet)

    assert worksheet.headers == SHEET_HEADERS


def test_upsert_appends_new_record():
    worksheet = FakeWorksheet()
    store = PanoramaSheetStore(worksheet)
    record = PanoramaLocation.from_form("PANO-001", "Lobby", "door", "hall")

    result = store.upsert(record)

    assert result == "created"
    assert worksheet.rows[0]["place_code"] == "PANO-001"


def test_upsert_updates_existing_place_hotspot_pair():
    worksheet = FakeWorksheet(
        rows=[
            {
                "place_code": "PANO-001",
                "place_name": "Lobby",
                "hotspot": "door",
                "connects_to": "old",
                "updated_at": "",
            }
        ]
    )
    store = PanoramaSheetStore(worksheet)
    record = PanoramaLocation.from_form("pano-001", "Lobby New", "DOOR", "new")

    result = store.upsert(record)

    assert result == "updated"
    assert worksheet.rows[0]["place_name"] == "Lobby New"
    assert worksheet.rows[0]["connects_to"] == "new"


def test_delete_removes_matching_record():
    worksheet = FakeWorksheet(
        rows=[
            {
                "place_code": "PANO-001",
                "place_name": "Lobby",
                "hotspot": "door",
                "connects_to": "hall",
                "updated_at": "",
            }
        ]
    )
    store = PanoramaSheetStore(worksheet)

    assert store.delete("pano-001", "DOOR") is True
    assert worksheet.rows == []

