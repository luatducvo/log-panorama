from __future__ import annotations

import pandas as pd
import streamlit as st

from log_panorama.models import PanoramaLocation, ValidationError
from log_panorama.sheets import PanoramaSheetStore, SheetConfigError, build_store_from_secrets


st.set_page_config(
    page_title="Panorama Log",
    page_icon="360",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def apply_mobile_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --surface: #ffffff;
            --soft: #f6f7f9;
            --border: #d9dee7;
            --ink: #17202a;
            --muted: #5b6675;
            --accent: #0f766e;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --surface: #1e2530;
                --soft: #262f3d;
                --border: #3a4556;
                --ink: #e8edf4;
                --muted: #9aa5b4;
                --accent: #2dd4bf;
            }
        }
        /* Streamlit dark theme override */
        [data-theme="dark"] {
            --surface: #1e2530;
            --soft: #262f3d;
            --border: #3a4556;
            --ink: #e8edf4;
            --muted: #9aa5b4;
            --accent: #2dd4bf;
        }
        .block-container {
            padding-top: 0.5rem;
            padding-bottom: 5rem;
            max-width: 980px;
        }
        /* Ẩn header toolbar mặc định của Streamlit */
        header[data-testid="stHeader"] {
            height: 0;
            min-height: 0;
            visibility: hidden;
        }
        div[data-testid="stDecoration"] {
            display: none;
        }
        h1, h2, h3, p, label, span {
            letter-spacing: 0;
            color: var(--ink) !important;
        }
        div[data-testid="stForm"] {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            padding: 1rem;
        }
        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] button {
            min-height: 44px;
            border-radius: 8px;
            font-weight: 650;
        }
        .stTextInput input,
        .stSelectbox div[data-baseweb="select"] {
            min-height: 44px;
            border-radius: 8px;
            background: var(--surface) !important;
            color: var(--ink) !important;
            border-color: var(--border) !important;
        }
        div[data-testid="stMetric"] {
            background: var(--soft);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.75rem;
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] div {
            color: var(--ink) !important;
        }
        div[data-testid="stCaption"],
        div[data-testid="stCaption"] p {
            color: var(--muted) !important;
        }
        div[data-testid="stExpander"] {
            border-color: var(--border) !important;
        }
        @media (max-width: 640px) {
            .block-container {
                padding-left: 0.75rem;
                padding-right: 0.75rem;
            }
            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }
            div[data-testid="stDataFrame"] {
                overflow-x: auto;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def get_store() -> PanoramaSheetStore:
    return build_store_from_secrets(st.secrets)


@st.cache_data(ttl=60, show_spinner=False)
def load_records(_store: PanoramaSheetStore) -> list[PanoramaLocation]:
    """Tải dữ liệu từ Google Sheets, cache tối đa 60 giây."""
    return _store.list_records()


def records_to_dataframe(records: list[PanoramaLocation]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Mã địa điểm": record.place_code,
                "Tên địa điểm": record.place_name,
                "Hotspot": record.hotspot,
                "Hotspot nối tới": record.connects_to,
                "Vĩ độ": record.latitude,
                "Kinh độ": record.longitude,
                "Cập nhật": record.updated_at,
            }
            for record in records
        ]
    )


def render_config_error(error: Exception) -> None:
    st.error(str(error))
    st.info(
        "Tạo file `.streamlit/secrets.toml` từ `.streamlit/secrets.example.toml`, "
        "điền service account, spreadsheet_id, rồi share Google Sheet cho client_email."
    )


KNOWN_PLACES: dict[str, str] = {
    "P360-GL-001": "Quảng trường Đại Đoàn Kết",
    "P360-GL-002": "Bảo tàng Gia Lai",
    "P360-GL-003": "Biển Hồ Pleiku",
    "P360-GL-004": "Chùa Minh Thành",
    "P360-GL-005": "Chùa Bửu Minh",
    "P360-GL-006": "Công viên Diên Hồng",
}


def render_form(store: PanoramaSheetStore, records: list[PanoramaLocation]) -> None:
    with st.form("location_form", clear_on_submit=False):
        # st.subheader("Quản lý log")

        # Merge known places with any extra codes already in the sheet
        sheet_map = {record.place_code: record.place_name for record in records}
        combined: dict[str, str] = {**KNOWN_PLACES, **sheet_map}
        quick_options = [""] + [
            f"{code} – {name}" for code, name in sorted(combined.items())
        ]
        selected_quick = st.selectbox(
            "Chọn nhanh địa điểm",
            quick_options,
            index=0,
        )
        selected_code = selected_quick.split(" – ")[0] if selected_quick else ""

        place_code = selected_code
        known_name = combined.get(selected_code, "")
        place_name = st.text_input("Tên địa điểm", value=known_name, placeholder="VD: Sảnh chính")

        hotspot = st.text_input("Hotspot của địa điểm", placeholder="VD: CMT-EXT-001")
        st.caption(
            "**Quy tắc đặt tên hotspot:** `[Mã địa điểm]-[Khu vực]-[Số thứ tự]`  \n"
            "• **Mã địa điểm** — viết tắt tên địa điểm, VD: `CMT` = Chùa Minh Thành  \n"
            "• **Khu vực** — `EXT` ngoài trời · `INT` bên trong  \n"
            "• **Số thứ tự** — 3 chữ số, VD: `001`, `002`"
        )
        connects_to = st.text_input("Hotspot nối tới", placeholder="VD: CMT-EXT-001")

        lat_col, lon_col = st.columns(2)
        with lat_col:
            latitude = st.text_input("Vĩ độ (Latitude)", placeholder="VD: 13.9833")
        with lon_col:
            longitude = st.text_input("Kinh độ (Longitude)", placeholder="VD: 108.0000")

        submitted = st.form_submit_button("Lưu vào Google Sheet", width='stretch')

    if not submitted:
        return

    try:
        record = PanoramaLocation.from_form(place_code, place_name, hotspot, connects_to, latitude, longitude)
        result = store.upsert(record)
    except ValidationError as exc:
        st.warning(str(exc))
        return
    except Exception as exc:
        st.error(f"Không lưu được vào Google Sheet: {exc}")
        return

    load_records.clear()
    message = "Đã tạo log mới." if result == "created" else "Đã cập nhật log hiện có."
    st.success(message)
    st.rerun()


def render_debug(store: PanoramaSheetStore) -> None:
    """Panel debug — chỉ hiện khi bật trong query params hoặc secrets."""
    show_debug = st.query_params.get("debug") == "1"
    if not show_debug:
        return

    with st.expander("🛠 Debug info", expanded=True):
        try:
            raw_rows = store.worksheet.get_all_records()
            st.write(f"**Số dòng raw từ sheet:** {len(raw_rows)}")
            if raw_rows:
                st.write("**Header keys của dòng đầu:**", list(raw_rows[0].keys()))
                st.write("**Dòng đầu tiên:**", raw_rows[0])
            else:
                first_row = store.worksheet.row_values(1)
                st.write("**Row 1 (raw):**", first_row)
                st.write("**SHEET_HEADERS expected:**", store.worksheet._spreadsheet is not None)
        except Exception as exc:
            st.error(f"Debug error: {exc}")


def render_records(store: PanoramaSheetStore, records: list[PanoramaLocation]) -> None:
    title_col, refresh_col = st.columns([4, 1])
    with title_col:
        st.subheader("Danh sách log")
    with refresh_col:
        if st.button("🔄 Làm mới", use_container_width=True, help="Tải lại dữ liệu mới nhất từ Google Sheets"):
            load_records.clear()
            st.rerun()

    search = st.text_input("Tìm kiếm", placeholder="Nhập mã, tên địa điểm, hotspot...")
    filtered = records
    if search.strip():
        needle = search.strip().casefold()
        filtered = [
            record
            for record in records
            if needle
            in " ".join(
                [record.place_code, record.place_name, record.hotspot, record.connects_to]
            ).casefold()
        ]

    metric_cols = st.columns(3)
    metric_cols[0].metric("Tổng log", len(records))
    metric_cols[1].metric("Địa điểm", len({record.place_code for record in records}))
    metric_cols[2].metric("Đang hiển thị", len(filtered))

    dataframe = records_to_dataframe(filtered)
    if dataframe.empty:
        st.info("Chưa có log nào phù hợp.")
    else:
        st.dataframe(dataframe, hide_index=True, width='stretch')

    with st.expander("✏️ Chỉnh sửa log"):
        if not records:
            st.caption("Chưa có dữ liệu để chỉnh sửa.")
        else:
            edit_options = {
                f"{r.place_code} | {r.hotspot}": r for r in records
            }
            edit_selected = st.selectbox(
                "Chọn log cần chỉnh sửa",
                list(edit_options.keys()),
                key="edit_select",
            )
            editing: PanoramaLocation = edit_options[edit_selected]

            with st.form("edit_form", clear_on_submit=False):
                st.caption(f"Đang chỉnh sửa: **{editing.place_code} | {editing.hotspot}**")

                edit_name = st.text_input("Tên địa điểm", value=editing.place_name)
                edit_hotspot = st.text_input("Hotspot của địa điểm", value=editing.hotspot)
                edit_connects_to = st.text_input("Hotspot nối tới", value=editing.connects_to)

                lat_col, lon_col = st.columns(2)
                with lat_col:
                    edit_lat = st.text_input("Vĩ độ (Latitude)", value=editing.latitude)
                with lon_col:
                    edit_lon = st.text_input("Kinh độ (Longitude)", value=editing.longitude)

                save_edit = st.form_submit_button("Lưu chỉnh sửa", width="stretch")

            if save_edit:
                try:
                    updated = PanoramaLocation.from_form(
                        editing.place_code, edit_name, edit_hotspot,
                        edit_connects_to, edit_lat, edit_lon,
                    )
                    # Nếu hotspot đổi tên → xóa record cũ trước
                    if updated.hotspot.casefold() != editing.hotspot.casefold():
                        store.delete(editing.place_code, editing.hotspot)
                    store.upsert(updated)
                except ValidationError as exc:
                    st.warning(str(exc))
                else:
                    load_records.clear()
                    st.success("Đã lưu chỉnh sửa.")
                    st.rerun()

    with st.expander("🗑️ Xóa log"):
        if not records:
            st.caption("Chưa có dữ liệu để xóa.")
            return

        options = {
            f"{record.place_code} | {record.hotspot} -> {record.connects_to or '-'}": record
            for record in records
        }
        selected = st.selectbox("Chọn log cần xóa", list(options.keys()))
        confirm = st.checkbox("Tôi muốn xóa log này")
        if st.button("Xóa log", type="secondary", width='stretch', disabled=not confirm):
            record = options[selected]
            if store.delete(record.place_code, record.hotspot):
                load_records.clear()
                st.success("Đã xóa log.")
                st.rerun()
            else:
                st.warning("Không tìm thấy log để xóa.")


def main() -> None:
    apply_mobile_styles()
    st.markdown(
        '<p style="font-size:1.1rem;font-weight:700;margin:0 0 0.1rem 0;color:var(--ink)">'
        'Panorama 360 Log</p>'
        '<p style="font-size:0.78rem;margin:0 0 0.75rem 0;color:var(--muted)">'
        'Quản lý hotspot địa điểm · Google Sheets</p>',
        unsafe_allow_html=True,
    )

    try:
        store = get_store()
        records = load_records(store)
    except (SheetConfigError, KeyError) as exc:
        render_config_error(exc)
        return
    except Exception as exc:
        st.error(f"Không kết nối được Google Sheets: {exc}")
        return

    render_form(store, records)
    st.divider()
    render_debug(store)
    render_records(store, records)


if __name__ == "__main__":
    main()

