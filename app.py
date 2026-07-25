from __future__ import annotations

import pandas as pd
import streamlit as st

from log_panorama.models import (
    Member,
    PanoramaLocation,
    PlaceCode,
    ValidationError,
    make_abbreviation,
    suggest_next_hotspot_number,
)
from log_panorama.sheets import (
    MemberSheetStore,
    PanoramaSheetStore,
    PlaceCodeSheetStore,
    SheetConfigError,
    build_stores,
)


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
        /* ===== Theme variables ===== */
        :root {
            --surface: #ffffff;
            --soft: #f6f7f9;
            --border: #d9dee7;
            --ink: #17202a;
            --muted: #5b6675;
            --accent: #0f766e;
            --shadow: 0 1px 3px rgba(0,0,0,0.08);
            color-scheme: light;
        }
        html[data-theme="dark"] {
            --surface: #1e2530;
            --soft: #262f3d;
            --border: #3a4556;
            --ink: #e8edf4;
            --muted: #9aa5b4;
            --accent: #2dd4bf;
            --shadow: 0 1px 3px rgba(0,0,0,0.3);
            color-scheme: dark;
        }
        @media (prefers-color-scheme: dark) {
            html:not([data-theme="light"]) {
                --surface: #1e2530;
                --soft: #262f3d;
                --border: #3a4556;
                --ink: #e8edf4;
                --muted: #9aa5b4;
                --accent: #2dd4bf;
                --shadow: 0 1px 3px rgba(0,0,0,0.3);
                color-scheme: dark;
            }
        }

        /* ===== Layout ===== */
        .block-container {
            padding-top: 0.5rem;
            padding-bottom: calc(5rem + env(safe-area-inset-bottom, 0px));
            max-width: 980px;
        }

        /* Hide Streamlit chrome */
        header[data-testid="stHeader"] {
            height: 0;
            min-height: 0;
            visibility: hidden;
        }
        div[data-testid="stDecoration"] {
            display: none;
        }

        /* ===== Typography ===== */
        h1, h2, h3, h4, p, label, span, li, strong, td, th {
            letter-spacing: 0;
            color: var(--ink) !important;
        }

        /* ===== Sticky app header ===== */
        .pano-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            position: sticky;
            top: 0;
            z-index: 100;
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            padding: 0.6rem 0;
            margin-bottom: 0.5rem;
        }
        .pano-title-main {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--ink);
            display: block;
            line-height: 1.3;
        }
        .pano-title-sub {
            font-size: 0.76rem;
            color: var(--muted);
            display: block;
            line-height: 1.3;
        }
        .pano-theme-btn {
            background: var(--soft);
            border: 1px solid var(--border);
            border-radius: 10px;
            width: 42px;
            height: 42px;
            font-size: 1.25rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            padding: 0;
            line-height: 1;
        }
        .pano-theme-btn:hover {
            border-color: var(--accent);
        }
        .pano-theme-btn:active {
            transform: scale(0.92);
        }
        .pano-theme-btn .icon-sun { display: none; }
        .pano-theme-btn .icon-moon { display: inline; }
        html[data-theme="dark"] .pano-theme-btn .icon-sun { display: inline; }
        html[data-theme="dark"] .pano-theme-btn .icon-moon { display: none; }

        /* ===== App background ===== */
        .stApp,
        section[data-testid="stMain"],
        section[data-testid="stSidebar"],
        div[data-testid="stAppViewContainer"],
        div[data-testid="stVerticalBlock"] {
            background-color: var(--surface);
        }

        /* ===== Forms ===== */
        div[data-testid="stForm"] {
            border: 1px solid var(--border);
            border-radius: 10px;
            background: var(--surface);
            padding: 1rem;
        }

        /* ===== Buttons ===== */
        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] button {
            min-height: 44px;
            border-radius: 8px;
            font-weight: 650;
        }

        /* ===== Text inputs ===== */
        .stTextInput input,
        .stSelectbox div[data-baseweb="select"] {
            min-height: 44px;
            border-radius: 8px;
            background: var(--surface) !important;
            color: var(--ink) !important;
            border-color: var(--border) !important;
        }
        .stTextInput input::placeholder {
            color: var(--muted) !important;
            opacity: 1;
        }
        .stTextInput input:focus {
            border-color: var(--accent) !important;
        }

        /* ===== Selectbox dropdown menu ===== */
        [data-baseweb="select"] span,
        [data-baseweb="select"] div {
            color: var(--ink) !important;
        }
        [data-baseweb="menu"] {
            background-color: var(--surface) !important;
            color: var(--ink) !important;
        }
        [data-baseweb="menu"] li {
            color: var(--ink) !important;
            background-color: var(--surface) !important;
        }
        [data-baseweb="menu"] li:hover,
        [data-baseweb="menu"] li[aria-selected="true"] {
            background-color: var(--soft) !important;
        }

        /* ===== Checkbox ===== */
        .stCheckbox label,
        .stCheckbox span,
        div[data-testid="stCheckbox"] span,
        div[data-testid="stCheckbox"] p {
            color: var(--ink) !important;
        }

        /* ===== Metrics ===== */
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

        /* ===== Captions ===== */
        div[data-testid="stCaption"],
        div[data-testid="stCaption"] p {
            color: var(--muted) !important;
        }

        /* ===== Expanders ===== */
        div[data-testid="stExpander"] {
            border-color: var(--border) !important;
            background: var(--surface);
        }
        div[data-testid="stExpander"] details,
        div[data-testid="stExpanderDetails"] {
            background: var(--surface) !important;
            border-color: var(--border) !important;
        }
        div[data-testid="stExpanderSummary"],
        div[data-testid="stExpander"] summary {
            color: var(--ink) !important;
            background: var(--surface);
        }
        div[data-testid="stExpanderDetails"] p,
        div[data-testid="stExpanderDetails"] span,
        div[data-testid="stExpanderDetails"] label {
            color: var(--ink) !important;
        }

        /* ===== Alert boxes (info, warning, error, success) ===== */
        div[data-testid="stAlert"],
        div[data-testid*="Alert"] {
            background-color: var(--soft) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px;
            color: var(--ink) !important;
        }
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span,
        div[data-testid*="Alert"] p,
        div[data-testid*="Alert"] span,
        div[data-testid*="Alert"] div {
            color: var(--ink) !important;
        }

        /* ===== Popover ===== */
        div[data-testid="stPopoverContent"] {
            background-color: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px;
        }
        div[data-testid="stPopoverContent"] p,
        div[data-testid="stPopoverContent"] span,
        div[data-testid="stPopoverContent"] label {
            color: var(--ink) !important;
        }

        /* ===== Tabs ===== */
        div[data-testid="stTabs"] [role="tablist"] {
            border-color: var(--border) !important;
            gap: 0.25rem;
        }
        div[data-testid="stTabs"] button[role="tab"] {
            color: var(--muted) !important;
            border-radius: 8px 8px 0 0;
        }
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: var(--accent) !important;
        }
        div[data-testid="stTabContent"] {
            background-color: var(--surface);
        }

        /* ===== Divider ===== */
        hr[data-testid="stDivider"],
        div[data-testid="stDivider"] hr {
            border-color: var(--border) !important;
        }

        /* ===== Dataframe ===== */
        div[data-testid="stDataFrame"] {
            background-color: var(--surface) !important;
            border: 1px solid var(--border);
            border-radius: 8px;
        }
        div[data-testid="stDataFrame"] [data-testid="data-grid"] {
            background-color: var(--surface) !important;
        }

        /* ===== SVG icons (selectbox arrows, etc.) ===== */
        .stSelectbox svg,
        div[data-baseweb="select"] svg {
            fill: var(--muted) !important;
            color: var(--muted) !important;
        }

        /* ===== Mobile responsive ===== */
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
            .pano-title-main { font-size: 1.05rem; }
            .pano-title-sub { font-size: 0.72rem; }
        }

        /* Hide JS-injection iframes */
        iframe[height="0"] {
            border: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_theme_script() -> None:
    st.components.v1.html(
        """
        <script>
        (function() {
            try {
                var doc = window.parent.document;
                var root = doc.documentElement;
                var KEY = 'pano-theme';
                function getTheme() {
                    var t = localStorage.getItem(KEY);
                    if (!t) {
                        t = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
                    }
                    return t;
                }
                function applyTheme() {
                    root.setAttribute('data-theme', getTheme());
                }
                applyTheme();
                if (!window.parent.__panoThemeInit) {
                    window.parent.__panoThemeInit = true;
                    doc.addEventListener('click', function(e) {
                        var btn = e.target.closest('#theme-toggle');
                        if (!btn) return;
                        e.preventDefault();
                        e.stopPropagation();
                        var cur = getTheme();
                        var next = cur === 'dark' ? 'light' : 'dark';
                        localStorage.setItem(KEY, next);
                        root.setAttribute('data-theme', next);
                    }, true);
                }
            } catch(err) {}
        })();
        </script>
        """,
        height=0,
    )


@st.cache_resource(show_spinner=False)
def get_stores() -> tuple[PanoramaSheetStore, PlaceCodeSheetStore, MemberSheetStore]:
    return build_stores(st.secrets)


@st.cache_data(ttl=60, show_spinner=False)
def load_records(_store: PanoramaSheetStore) -> list[PanoramaLocation]:
    return _store.list_records()


def load_places(_store: PlaceCodeSheetStore) -> list[PlaceCode]:
    places = _store.list_places()
    if not places:
        _seed_initial_places(_store)
        places = _store.list_places()
    return places


def load_members(_store: MemberSheetStore) -> list[Member]:
    return _store.list_members()


def _seed_initial_places(store: PlaceCodeSheetStore) -> None:
    initial = {
        "P360-GL-001": "Quảng trường Đại Đoàn Kết",
        "P360-GL-002": "Bảo tàng Gia Lai",
        "P360-GL-003": "Biển Hồ Pleiku",
        "P360-GL-004": "Chùa Minh Thành",
        "P360-GL-005": "Chùa Bửu Minh",
        "P360-GL-006": "Công viên Diên Hồng",
    }
    for code, name in initial.items():
        store.upsert(PlaceCode(code=code, name=name))


def records_to_dataframe(records: list[PanoramaLocation]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Mã địa điểm": record.place_code,
                "Mô tả địa điểm": record.place_name,
                "Hotspot": record.hotspot,
                "Hotspot nối": record.connects_to,
                "Thành viên": record.member,
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


def render_form(
    store: PanoramaSheetStore,
    place_store: PlaceCodeSheetStore,
    member_store: MemberSheetStore,
    records: list[PanoramaLocation],
    places: list[PlaceCode],
    members: list[Member],
) -> None:
    # Build lookup maps
    place_map = {p.code: p.name for p in places}
    sheet_map = {record.place_code: record.place_name for record in records}

    # Popover for adding new place code (outside form)
    col1, col2 = st.columns([4, 1])
    with col1:
        quick_options = [
            f"{p.code} – {p.name}" for p in sorted(places, key=lambda x: x.code)
        ]
        selected_quick = st.selectbox(
            "Chọn nhanh địa điểm",
            quick_options,
            index=0,
        )
        selected_code = selected_quick.split(" – ")[0] if selected_quick else ""
    with col2:
        st.write("")
        with st.popover("➕ Thêm mới"):
            new_code = st.text_input("Mã địa điểm", placeholder="VD: P360-CMT-001")
            new_desc = st.text_input("Mô tả địa điểm", placeholder="VD: Chùa Minh Thành")
            if st.button("Thêm vào danh sách", type="primary", use_container_width=True):
                if new_code.strip():
                    place_store.upsert(PlaceCode(code=new_code.strip(), name=new_desc.strip()))
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập mã địa điểm")

    # Member management
    mcol1, mcol2 = st.columns([4, 1])
    with mcol1:
        member_options = [""] + sorted(
            [f"{m.code} – {m.name}" for m in members],
            key=lambda x: x.casefold(),
        )
        member = st.selectbox(
            "Thành viên phụ trách",
            member_options,
            format_func=lambda x: "— Chọn thành viên —" if not x else x,
        )
    with mcol2:
        st.write("")
        with st.popover("👤 Quản lý"):
            add_tab, edit_tab, del_tab = st.tabs(["Thêm", "Sửa", "Xoá"])
            with add_tab:
                new_member_code = st.text_input("Mã thành viên", placeholder="VD: NV001", key="new_member_code")
                new_member_name = st.text_input("Tên thành viên", placeholder="VD: Nguyễn Văn A", key="new_member_name")
                if st.button("Thêm", type="primary", use_container_width=True):
                    if new_member_code.strip():
                        member_store.upsert(Member(code=new_member_code.strip(), name=new_member_name.strip()))
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.warning("Vui lòng nhập mã thành viên")
            with edit_tab:
                if members:
                    edit_opts = {f"{m.code} – {m.name}": m for m in sorted(members, key=lambda x: x.code)}
                    member_to_edit = st.selectbox("Chọn thành viên", list(edit_opts.keys()), key="member_edit_select")
                    sm = edit_opts[member_to_edit]
                    edit_member_name = st.text_input("Tên mới", value=sm.name, key="edit_member_name")
                    if st.button("Cập nhật", type="primary", use_container_width=True):
                        member_store.upsert(Member(code=sm.code, name=edit_member_name.strip()))
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.caption("Chưa có thành viên nào.")
            with del_tab:
                if members:
                    del_opts = {f"{m.code} – {m.name}": m for m in sorted(members, key=lambda x: x.code)}
                    member_to_del = st.selectbox("Chọn thành viên", list(del_opts.keys()), key="member_del_select")
                    if st.button("Xoá", type="secondary", use_container_width=True):
                        md = del_opts[member_to_del]
                        if member_store.delete(md.code):
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.warning("Không tìm thấy thành viên.")
                else:
                    st.caption("Chưa có thành viên nào.")

    # Auto-generate abbreviation from place name
    place_full_name = place_map.get(selected_code, "")
    abbreviation = make_abbreviation(place_full_name)

    zone = st.selectbox(
        "Khu vực",
        ["", "EXT", "INT"],
        key="zone_select",
        format_func=lambda x: {"": "— Chọn khu vực —", "EXT": "EXT – Ngoài trời", "INT": "INT – Bên trong"}.get(x, x),
    )

    if abbreviation and zone:
        next_num = suggest_next_hotspot_number(records, abbreviation, zone)
        hotspot_value = f"{abbreviation}-{zone}-{next_num}"
        st.info(f"Hotspot: **{hotspot_value}**")
    else:
        hotspot_value = ""

    with st.form("location_form", clear_on_submit=False):
        place_code = selected_code
        place_name = st.text_input("Mô tả địa điểm", placeholder="VD: Cổng chính")

        same_abbr_hotspots = sorted(
            r.hotspot for r in records
            if r.hotspot.casefold().startswith(abbreviation.casefold())
            and r.hotspot != hotspot_value
        )
        connects_to = st.selectbox(
            "Hotspot nối",
            [""] + same_abbr_hotspots,
            format_func=lambda x: "— Không kết nối —" if not x else x,
        )

        lat_col, lon_col = st.columns(2)
        with lat_col:
            latitude = st.text_input("Vĩ độ (Latitude)", placeholder="VD: 13.9833")
        with lon_col:
            longitude = st.text_input("Kinh độ (Longitude)", placeholder="VD: 108.0000")

        submitted = st.form_submit_button("Lưu vào Google Sheet", type="primary", width='stretch')

    if not submitted:
        return

    if not hotspot_value:
        st.warning("Vui lòng chọn khu vực (EXT/INT)")
        return

    member_code = member.split(" – ")[0] if member else ""
    try:
        record = PanoramaLocation.from_form(place_code, place_name, hotspot_value, connects_to, member_code, latitude, longitude)
        result = store.upsert(record)
    except ValidationError as exc:
        st.warning(str(exc))
        return
    except Exception as exc:
        st.error(f"Không lưu được vào Google Sheet: {exc}")
        return

    st.cache_data.clear()
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


def render_records(store: PanoramaSheetStore, records: list[PanoramaLocation], places: list[PlaceCode], members: list[Member]) -> None:
    title_col, refresh_col = st.columns([4, 1])
    with title_col:
        st.subheader("Danh sách log")
    with refresh_col:
        if st.button("🔄 Làm mới", use_container_width=True, key="refresh_btn"):
            st.cache_data.clear()
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

            # Parse existing hotspot for zone
            edit_parts = editing.hotspot.split("-")
            edit_zone_current = edit_parts[1] if len(edit_parts) >= 2 and edit_parts[1] in ("EXT", "INT") else ""

            # Compute abbreviation from place name
            edit_place_map = {p.code: p.name for p in places}
            edit_place_full_name = edit_place_map.get(editing.place_code, "")
            edit_abbreviation = make_abbreviation(edit_place_full_name)

            edit_zone = st.selectbox(
                "Khu vực",
                ["", "EXT", "INT"],
                index=["", "EXT", "INT"].index(edit_zone_current) if edit_zone_current in ("EXT", "INT") else 0,
                key="edit_zone",
                format_func=lambda x: {"": "— Chọn khu vực —", "EXT": "EXT – Ngoài trời", "INT": "INT – Bên trong"}.get(x, x),
            )

            if edit_abbreviation and edit_zone:
                edit_next_num = suggest_next_hotspot_number(records, edit_abbreviation, edit_zone)
                edit_hotspot_value = f"{edit_abbreviation}-{edit_zone}-{edit_next_num}"
                st.info(f"Hotspot: **{edit_hotspot_value}**")
            else:
                edit_hotspot_value = ""

            with st.form("edit_form", clear_on_submit=False):
                st.caption(f"Đang chỉnh sửa: **{editing.place_code} | {editing.hotspot}**")

                edit_name = st.text_input("Mô tả địa điểm", value=editing.place_name)

                same_abbr_hotspots = sorted(
                    r.hotspot for r in records
                    if r.hotspot.casefold().startswith(edit_abbreviation.casefold())
                    and r.hotspot != editing.hotspot
                )
                edit_connects_options = [""] + same_abbr_hotspots
                edit_connects_index = 0
                if editing.connects_to in edit_connects_options:
                    edit_connects_index = edit_connects_options.index(editing.connects_to)
                edit_connects_to = st.selectbox(
                    "Hotspot nối",
                    edit_connects_options,
                    index=edit_connects_index,
                    format_func=lambda x: "— Không kết nối —" if not x else x,
                )

                edit_member_options = [""] + sorted(
                    [f"{m.code} – {m.name}" for m in members],
                    key=lambda x: x.casefold(),
                )
                edit_member_index = 0
                edit_member_display = ""
                if editing.member:
                    for i, opt in enumerate(edit_member_options):
                        if opt.startswith(editing.member + " –"):
                            edit_member_index = i
                            edit_member_display = opt
                            break
                edit_member = st.selectbox(
                    "Thành viên",
                    edit_member_options,
                    index=edit_member_index,
                    format_func=lambda x: "— Chọn thành viên —" if not x else x,
                )

                lat_col, lon_col = st.columns(2)
                with lat_col:
                    edit_lat = st.text_input("Vĩ độ (Latitude)", value=editing.latitude)
                with lon_col:
                    edit_lon = st.text_input("Kinh độ (Longitude)", value=editing.longitude)

                save_edit = st.form_submit_button("Lưu chỉnh sửa", type="primary", width="stretch")

            if save_edit:
                if not edit_hotspot_value:
                    st.warning("Vui lòng chọn khu vực (EXT/INT)")
                else:
                    edit_member_code = edit_member.split(" – ")[0] if edit_member else ""
                    try:
                        updated = PanoramaLocation.from_form(
                            editing.place_code, edit_name, edit_hotspot_value,
                            edit_connects_to, edit_member_code, edit_lat, edit_lon,
                        )
                        if updated.hotspot.casefold() != editing.hotspot.casefold():
                            store.delete(editing.place_code, editing.hotspot)
                        store.upsert(updated)
                    except ValidationError as exc:
                        st.warning(str(exc))
                    else:
                        st.cache_data.clear()
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
                st.cache_data.clear()
                st.success("Đã xóa log.")
                st.rerun()
            else:
                st.warning("Không tìm thấy log để xóa.")


def main() -> None:
    apply_mobile_styles()
    st.markdown(
        '<div class="pano-header">'
        '<div>'
        '<span class="pano-title-main">Panorama 360 Log</span>'
        '<span class="pano-title-sub">Quản lý hotspot · Google Sheets</span>'
        '</div>'
        '<button id="theme-toggle" class="pano-theme-btn" '
        'aria-label="Đổi giao diện sáng/tối" title="Sáng / Tối">'
        '<span class="icon-moon">🌙</span>'
        '<span class="icon-sun">☀️</span>'
        '</button>'
        '</div>',
        unsafe_allow_html=True,
    )
    inject_theme_script()

    try:
        store, place_store, member_store = get_stores()
        records = load_records(store)
        places = load_places(place_store)
        members = load_members(member_store)
    except (SheetConfigError, KeyError) as exc:
        render_config_error(exc)
        return
    except Exception as exc:
        st.error(f"Không kết nối được Google Sheets: {exc}")
        return

    render_form(store, place_store, member_store, records, places, members)
    st.divider()
    render_debug(store)
    render_records(store, records, places, members)


if __name__ == "__main__":
    main()

