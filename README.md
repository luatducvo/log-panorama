# Panorama 360 Log

Streamlit app de quan ly log dia diem anh 360 panorama va luu du lieu vao Google Sheets.

## Chay local

```powershell
uv sync
uv run streamlit run app.py
```

## Cau hinh Google Sheets

1. Tao Google Cloud service account va bat Google Sheets API.
2. Tao file `.streamlit/secrets.toml` theo mau `.streamlit/secrets.example.toml`.
3. Dien `spreadsheet_id`, `worksheet_name`, va thong tin service account.
4. Share Google Sheet cho email trong `client_email` voi quyen Editor.

Hai worksheet se duoc tao neu chua ton tai:
- `panorama_logs` (co the cau hinh bang `worksheet_name`) — luu log hotspot
- `place_codes` (co the cau hinh bang `place_codes_worksheet_name`) — danh sach ma dia diem

Headers cua `panorama_logs`:

```text
Mã địa điểm, Mô tả địa điểm, Hotspot, Hotspot nối tới, Vĩ độ, Kinh độ, Cập nhật
```

## Kiem thu

```powershell
uv run pytest
```
