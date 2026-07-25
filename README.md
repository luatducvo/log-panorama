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

Worksheet se duoc tao neu chua ton tai. Hang dau tien gom:

```text
place_code, place_name, hotspot, connects_to, updated_at
```

## Kiem thu

```powershell
uv run pytest
```
