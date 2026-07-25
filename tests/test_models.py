import pytest

from log_panorama.models import PanoramaLocation, ValidationError, normalize_sheet_records


def test_from_form_trims_values_and_sets_timestamp():
    record = PanoramaLocation.from_form(
        place_code=" PANO-001 ",
        place_name=" Lobby ",
        hotspot=" door-east ",
        connects_to=" hall-west ",
    )

    assert record.place_code == "PANO-001"
    assert record.place_name == "Lobby"
    assert record.hotspot == "door-east"
    assert record.connects_to == "hall-west"
    assert record.updated_at


def test_from_form_requires_place_code_name_and_hotspot():
    with pytest.raises(ValidationError) as exc:
        PanoramaLocation.from_form("", " ", "")

    assert "mã địa điểm" in str(exc.value)
    assert "mô tả địa điểm" in str(exc.value)
    assert "hotspot của địa điểm" in str(exc.value)


def test_make_abbreviation():
    from log_panorama.models import make_abbreviation

    assert make_abbreviation("Quảng trường Đại Đoàn Kết") == "QTĐĐK"
    assert make_abbreviation("Bảo tàng Gia Lai") == "BTGL"
    assert make_abbreviation("Biển Hồ Pleiku") == "BHP"
    assert make_abbreviation("Chùa Minh Thành") == "CMT"
    assert make_abbreviation("Công viên Diên Hồng") == "CVDH"
    assert make_abbreviation("") == ""
    assert make_abbreviation("Lobby") == "L"


def test_suggest_next_hotspot_number():
    from log_panorama.models import PanoramaLocation, suggest_next_hotspot_number

    records = [
        PanoramaLocation(place_code="P360-GL-001", place_name="Test", hotspot="QTĐĐK-EXT-001"),
        PanoramaLocation(place_code="P360-GL-001", place_name="Test", hotspot="QTĐĐK-EXT-002"),
        PanoramaLocation(place_code="P360-GL-001", place_name="Test", hotspot="QTĐĐK-INT-001"),
        PanoramaLocation(place_code="P360-GL-002", place_name="Test", hotspot="BTGL-EXT-005"),
    ]

    assert suggest_next_hotspot_number(records, "QTĐĐK", "EXT") == "003"
    assert suggest_next_hotspot_number(records, "QTĐĐK", "INT") == "002"
    assert suggest_next_hotspot_number(records, "BTGL", "EXT") == "006"
    assert suggest_next_hotspot_number(records, "CVDH", "EXT") == "001"
    assert suggest_next_hotspot_number([], "QTĐĐK", "EXT") == "001"


def test_member_from_sheet_row():
    from log_panorama.models import Member

    row = {"Mã thành viên": " NV001 ", "Tên thành viên": "  Nguyễn Văn A  "}
    m = Member.from_sheet_row(row)
    assert m.code == "NV001"
    assert m.name == "Nguyễn Văn A"


def test_member_key_is_casefold_code():
    from log_panorama.models import Member

    assert Member(code="NV001").key == "nv001"


def test_member_to_sheet_row():
    from log_panorama.models import Member

    assert Member(code="NV001", name="Nguyễn Văn A").to_sheet_row() == ["NV001", "Nguyễn Văn A"]


def test_panorama_location_default_member_is_empty():
    from log_panorama.models import PanoramaLocation

    loc = PanoramaLocation(place_code="P001", place_name="Test", hotspot="H001")
    assert loc.member == ""


def test_panorama_location_from_form_accepts_member():
    loc = PanoramaLocation.from_form("P001", "Test", "H001", member="NV001")
    assert loc.member == "NV001"


def test_panorama_location_to_sheet_row_includes_member():
    loc = PanoramaLocation.from_form("P001", "Test", "H001", member="NV001")
    row = loc.to_sheet_row()
    assert row[4] == "NV001"


def test_panorama_location_from_sheet_row_reads_member():
    row = {
        "Mã địa điểm": "P001",
        "Mô tả địa điểm": "Test",
        "Hotspot": "H001",
        "Thành viên": "NV001",
    }
    loc = PanoramaLocation.from_sheet_row(row)
    assert loc.member == "NV001"


def test_normalize_sheet_records_skips_empty_rows():
    records = normalize_sheet_records(
        [
            {"Mã địa điểm": "PANO-001", "Mô tả địa điểm": "Lobby", "Hotspot": "door"},
            {"Mã địa điểm": "", "Mô tả địa điểm": "", "Hotspot": ""},
        ]
    )

    assert len(records) == 1
    assert records[0].place_code == "PANO-001"

