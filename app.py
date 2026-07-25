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
        .block-container {
            padding-top: 1rem;
            padding-bottom: 5rem;
            max-width: 980px;
        }
        h1, h2, h3, p, label, span {
            letter-spacing: 0;
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
        .stTextInput input {
            min-height: 44px;
            border-radius: 8px;
        }
        div[data-testid="stMetric"] {
            background: var(--soft);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.75rem;
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


def load_records(store: PanoramaSheetStore) -> list[PanoramaLocation]:
    return store.list_records()


def records_to_dataframe(records: list[PanoramaLocation]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Ma dia diem": record.place_code,
                "Ten dia diem": record.place_name,
                "Hotspot": record.hotspot,
                "Hotspot noi toi": record.connects_to,
                "Cap nhat": record.updated_at,
            }
            for record in records
        ]
    )


def render_config_error(error: Exception) -> None:
    st.error(str(error))
    st.info(
        "Tao file `.streamlit/secrets.toml` tu `.streamlit/secrets.example.toml`, "
        "dien service account, spreadsheet_id, roi share Google Sheet cho client_email."
    )


def render_form(store: PanoramaSheetStore, records: list[PanoramaLocation]) -> None:
    with st.form("location_form", clear_on_submit=False):
        st.subheader("Them hoac cap nhat log")

        recent_codes = sorted({record.place_code for record in records})
        selected_code = st.selectbox(
            "Chon nhanh ma dia diem da co",
            [""] + recent_codes,
            index=0,
        )

        code_col, name_col = st.columns(2)
        with code_col:
            place_code = st.text_input("Ma dia diem", value=selected_code, placeholder="VD: PANO-001")
        with name_col:
            known_name = next(
                (record.place_name for record in records if record.place_code == selected_code),
                "",
            )
            place_name = st.text_input("Ten dia diem", value=known_name, placeholder="VD: Sanh chinh")

        hotspot = st.text_input("Hotspot cua dia diem", placeholder="VD: cua-ra-vao")
        connects_to = st.text_input("Hotspot noi toi", placeholder="VD: hanh-lang-01")

        submitted = st.form_submit_button("Luu vao Google Sheet", use_container_width=True)

    if not submitted:
        return

    try:
        record = PanoramaLocation.from_form(place_code, place_name, hotspot, connects_to)
        result = store.upsert(record)
    except ValidationError as exc:
        st.warning(str(exc))
        return
    except Exception as exc:
        st.error(f"Khong luu duoc vao Google Sheet: {exc}")
        return

    st.cache_resource.clear()
    message = "Da tao log moi." if result == "created" else "Da cap nhat log hien co."
    st.success(message)
    st.rerun()


def render_records(store: PanoramaSheetStore, records: list[PanoramaLocation]) -> None:
    st.subheader("Danh sach log")

    search = st.text_input("Tim kiem", placeholder="Nhap ma, ten dia diem, hotspot...")
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
    metric_cols[0].metric("Tong log", len(records))
    metric_cols[1].metric("Dia diem", len({record.place_code for record in records}))
    metric_cols[2].metric("Dang hien thi", len(filtered))

    dataframe = records_to_dataframe(filtered)
    if dataframe.empty:
        st.info("Chua co log nao phu hop.")
    else:
        st.dataframe(dataframe, hide_index=True, use_container_width=True)

    with st.expander("Xoa log"):
        if not records:
            st.caption("Chua co du lieu de xoa.")
            return

        options = {
            f"{record.place_code} | {record.hotspot} -> {record.connects_to or '-'}": record
            for record in records
        }
        selected = st.selectbox("Chon log can xoa", list(options.keys()))
        confirm = st.checkbox("Toi muon xoa log nay")
        if st.button("Xoa log", type="secondary", use_container_width=True, disabled=not confirm):
            record = options[selected]
            if store.delete(record.place_code, record.hotspot):
                st.cache_resource.clear()
                st.success("Da xoa log.")
                st.rerun()
            else:
                st.warning("Khong tim thay log de xoa.")


def main() -> None:
    apply_mobile_styles()
    st.title("Panorama 360 Log")
    st.caption("Quan ly ma dia diem, hotspot hien tai va hotspot noi toi tren Google Sheets.")

    try:
        store = get_store()
        records = load_records(store)
    except (SheetConfigError, KeyError) as exc:
        render_config_error(exc)
        return
    except Exception as exc:
        st.error(f"Khong ket noi duoc Google Sheets: {exc}")
        return

    render_form(store, records)
    st.divider()
    render_records(store, records)


if __name__ == "__main__":
    main()

