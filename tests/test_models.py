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


def test_normalize_sheet_records_skips_empty_rows():
    records = normalize_sheet_records(
        [
            {"Mã địa điểm": "PANO-001", "Mô tả địa điểm": "Lobby", "Hotspot": "door"},
            {"Mã địa điểm": "", "Mô tả địa điểm": "", "Hotspot": ""},
        ]
    )

    assert len(records) == 1
    assert records[0].place_code == "PANO-001"

