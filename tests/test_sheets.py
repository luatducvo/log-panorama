from log_panorama.models import MEMBER_HEADERS, Member, PLACE_HEADERS, PanoramaLocation, SHEET_HEADERS
from log_panorama.sheets import MemberSheetStore, PanoramaSheetStore


class FakeWorksheet:
    def __init__(self, rows=None, headers=None):
        self.headers = headers or SHEET_HEADERS
        self.rows = rows or []
        self.updated_ranges = []

    def row_values(self, row_index):
        return self.headers if row_index == 1 else []

    def update(self, range_name, values):
        self.updated_ranges.append((range_name, values))
        parts = range_name.split(":")
        col_end = parts[1][0]
        row_end = int(parts[1][1:])
        if row_end == 1:
            self.headers = values[0]
            return

        row_number = int(parts[0][1:])
        self.rows[row_number - 2] = dict(zip(self.headers, values[0], strict=True))

    def get_all_records(self):
        return self.rows

    def append_row(self, values, value_input_option=None):
        self.rows.append(dict(zip(self.headers, values, strict=True)))

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
    assert worksheet.rows[0]["Mã địa điểm"] == "PANO-001"


def test_upsert_updates_existing_place_hotspot_pair():
    worksheet = FakeWorksheet(
        rows=[
            {
                "Mã địa điểm": "PANO-001",
                "Mô tả địa điểm": "Lobby",
                "Hotspot": "door",
                "Hotspot nối": "old",
                "Cập nhật": "",
            }
        ]
    )
    store = PanoramaSheetStore(worksheet)
    record = PanoramaLocation.from_form("pano-001", "Lobby New", "DOOR", "new")

    result = store.upsert(record)

    assert result == "updated"
    assert worksheet.rows[0]["Mô tả địa điểm"] == "Lobby New"
    assert worksheet.rows[0]["Hotspot nối"] == "new"


def test_member_store_repairs_missing_headers():
    worksheet = FakeWorksheet(headers=[])
    store = MemberSheetStore(worksheet)
    assert worksheet.headers == MEMBER_HEADERS


def test_member_store_upsert_appends_new():
    worksheet = FakeWorksheet(headers=MEMBER_HEADERS)
    store = MemberSheetStore(worksheet)
    result = store.upsert(Member(code="NV001", name="Nguyễn Văn A"))
    assert result == "created"
    assert worksheet.rows[0]["Mã thành viên"] == "NV001"


def test_member_store_delete():
    worksheet = FakeWorksheet(
        rows=[{"Mã thành viên": "NV001", "Tên thành viên": "Nguyễn Văn A"}],
        headers=MEMBER_HEADERS,
    )
    store = MemberSheetStore(worksheet)
    assert store.delete("NV001") is True
    assert worksheet.rows == []


def test_delete_removes_matching_record():
    worksheet = FakeWorksheet(
        rows=[
            {
                "Mã địa điểm": "PANO-001",
                "Mô tả địa điểm": "Lobby",
                "Hotspot": "door",
                "Hotspot nối": "hall",
                "Cập nhật": "",
            }
        ]
    )
    store = PanoramaSheetStore(worksheet)

    assert store.delete("pano-001", "DOOR") is True
    assert worksheet.rows == []

