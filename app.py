
import streamlit as st
import pandas as pd

from dashboard_pages import (
    render_chart_builder,
    render_data_explorer,
    render_data_quality,
    render_overview,
)
from data_utils import buat_data_dummy

# ==================================================
# 1. KONFIGURASI DAN TAMPILAN
# ==================================================
st.set_page_config(
    page_title="MindScope | Mental Health Dashboard",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');

.stApp {
    background: #F5F7FC;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background: #172044;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 1500px;
}
.hero {
    background: #172044;
    padding: 28px 32px;
    border-radius: 14px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 8px 24px rgba(25, 39, 85, .12);
}
.hero h1 {
    color: white;
    font-family: 'Manrope', sans-serif;
    font-size: 2.5rem;
    margin: 5px 0;
}
.hero p {
    color: #E6E9FF;
    margin-bottom: 0;
}
.section-title {
    color: #20294B;
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 1.25rem;
    margin-top: 10px;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E6EAF4;
    border-radius: 12px;
    padding: 17px;
    box-shadow: 0 4px 16px rgba(25, 39, 85, .04);
}
div[data-testid="stMetricLabel"] {
    color: #6B7590;
}
div[data-testid="stMetricValue"] {
    color: #20294B;
}
div[data-testid="stTabs"] {
    display: none;
}
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}
.sidebar-mark {
    display: inline-flex;
    width: 30px;
    height: 30px;
    align-items: center;
    justify-content: center;
    border: 1px solid #8590ff;
    border-radius: 8px;
    color: #ffffff;
    font-weight: 800;
}
.sidebar-heading {
    color: #aeb8e8;
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin: 20px 0 8px;
}
.svg-icon {
    display: inline-flex;
    width: 24px;
    height: 24px;
    vertical-align: middle;
    color: #5965DC;
    margin-right: 8px;
}
.svg-icon svg {
    width: 100%;
    height: 100%;
}
</style>
""", unsafe_allow_html=True)


def svg_icon(name):
    icons = {
        "filter": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16M7 12h10M10 19h4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
        "summary": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M8 15v-3M12 15V8M16 15v-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
    }
    return f'<span class="svg-icon">{icons[name]}</span>'


# ==================================================
# 3. HEADER DASHBOARD

# ==================================================
st.markdown("""
<div class="hero">
    <p>DATA EXPLORATION STUDIO</p>
    <h1>MindScope</h1>
    <p>
        Interactive Mental Health Analytics Dashboard
        — eksplorasi data, ubah grafik, dan temukan pola
        dengan cara yang fleksibel.
    </p>
</div>
""", unsafe_allow_html=True)


# ==================================================
# 4. SIDEBAR DAN INPUT DATA
# ==================================================
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand"><span class="sidebar-mark">M</span>'
        '<strong>MindScope</strong></div>',
        unsafe_allow_html=True
    )
    st.caption("Atur sumber data dan preferensi analisis.")

    st.markdown('<div class="sidebar-heading">Navigasi</div>',
                unsafe_allow_html=True)
    bagian = st.radio(
        "Navigasi dashboard",
        ["Overview", "Chart Builder", "Data Explorer", "Data Quality"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-heading">Data</div>',
                unsafe_allow_html=True)
    sumber = st.radio(
        "Sumber Dataset",
        ["Dataset Demo", "Upload CSV Sendiri"]
    )

    file_csv = None
    buat_data_baru = False

    if sumber == "Upload CSV Sendiri":
        file_csv = st.file_uploader(
            "Upload file CSV",
            type=["csv"]
        )
    else:
        buat_data_baru = st.button(
            "Buat data demo baru",
            use_container_width=True,
            help=(
                "Buat variasi dataset demo baru. "
                "Data tidak berubah saat berpindah halaman "
                "atau mengubah filter."
            ),
        )

    st.divider()

    st.markdown('<div class="sidebar-heading">Pengaturan</div>',
                unsafe_allow_html=True)
    tampilkan_tabel = st.toggle(
        "Tampilkan tabel data",
        value=True
    )
    tampilkan_insight = st.toggle(
        "Tampilkan ringkasan otomatis",
        value=True
    )

    st.caption(
        "Data demo hanya untuk latihan, bukan data klinis."
    )


# ==================================================
# 5. MEMBACA DATA
# ==================================================
if sumber == "Dataset Demo":
    if (
        "dataset_demo" not in st.session_state
        or buat_data_baru
    ):
        st.session_state["dataset_demo"] = buat_data_dummy()

    df_asli = st.session_state["dataset_demo"].copy()

else:
    if file_csv is None:
        st.info(
            "Upload file CSV melalui sidebar "
            "untuk mulai menganalisis data."
        )
        st.stop()

    try:
        df_asli = pd.read_csv(file_csv)

    except UnicodeDecodeError:
        file_csv.seek(0)
        df_asli = pd.read_csv(
            file_csv,
            encoding="latin-1"
        )

    except Exception as e:
        st.error(f"Gagal membaca CSV: {e}")
        st.stop()

if df_asli.empty:
    st.warning("Dataset tidak memiliki baris data.")
    st.stop()

df_asli.columns = [
    str(c).strip() for c in df_asli.columns
]
df_asli = df_asli.dropna(axis=1, how="all")

if df_asli.columns.duplicated().any():
    st.error(
        "Ada nama kolom duplikat. "
        "Perbaiki nama kolom pada CSV terlebih dahulu."
    )
    st.stop()

kolom_numerik = df_asli.select_dtypes(
    include="number"
).columns.tolist()

kolom_kategori = [
    c for c in df_asli.columns
    if c not in kolom_numerik
]


# ==================================================
# 6. FILTER INTERAKTIF
# ==================================================
st.markdown(
    f'{svg_icon("filter")}<p class="section-title">Filter Data</p>',
    unsafe_allow_html=True
)

st.caption(
    "Pilih kategori atau rentang nilai. "
    "Ringkasan dan grafik akan mengikuti filter."
)

filter_data = {}

kolom_filter = st.columns(4)

for i, kolom in enumerate(kolom_kategori[:4]):
    with kolom_filter[i]:
        pilihan = sorted(
            df_asli[kolom]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        terpilih = st.multiselect(
            kolom.replace("_", " ").title(),
            pilihan,
            default=[],
            key=f"filter_{kolom}"
        )

        if terpilih:
            filter_data[kolom] = terpilih

with st.expander("Filter numerik"):
    kolom_filter_num = st.columns(3)

    for i, kolom in enumerate(kolom_numerik):
        seri = pd.to_numeric(
            df_asli[kolom], errors="coerce"
        ).dropna()

        if seri.empty or seri.min() == seri.max():
            continue

        nilai_min = float(seri.min())
        nilai_max = float(seri.max())

        with kolom_filter_num[i % 3]:
            rentang = st.slider(
                kolom.replace("_", " ").title(),
                min_value=nilai_min,
                max_value=nilai_max,
                value=(nilai_min, nilai_max),
                key=f"rentang_{kolom}"
            )

            if rentang != (nilai_min, nilai_max):
                filter_data[kolom] = rentang


df = df_asli.copy()

for kolom, pilihan in filter_data.items():
    if isinstance(pilihan, tuple):
        angka = pd.to_numeric(
            df[kolom], errors="coerce"
        )
        df = df[angka.between(pilihan[0], pilihan[1])]
    else:
        df = df[
            df[kolom].astype(str).isin(pilihan)
        ]

if df.empty:
    st.warning(
        "Tidak ada data yang cocok dengan filter. "
        "Ubah atau kosongkan filter."
    )
    st.stop()


# ==================================================
# 7. KPI / RINGKASAN UTAMA
# ==================================================
st.markdown(
    f'{svg_icon("summary")}<p class="section-title">Ringkasan Dataset</p>',
    unsafe_allow_html=True
)

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Jumlah Responden",
    f"{len(df):,}",
    delta=f"{len(df) - len(df_asli):+,} dari data awal"
)

k2.metric("Jumlah Variabel", f"{df.shape[1]:,}")

jumlah_kosong = int(df.isna().sum().sum())
k3.metric("Sel Kosong", f"{jumlah_kosong:,}")

if kolom_numerik:
    kolom_skor = next(
        (
            c for c in kolom_numerik
            if any(k in c.lower() for k in [
                "stres", "stress", "kecemasan",
                "anxiety", "depresi", "depression"
            ])
        ),
        kolom_numerik[0]
    )

    rata = pd.to_numeric(
        df[kolom_skor], errors="coerce"
    ).mean()

    k4.metric(
        f"Rata-rata {kolom_skor.replace('_', ' ')}",
        "—" if pd.isna(rata) else f"{rata:.2f}"
    )
else:
    k4.metric("Kolom Numerik", "0")


# ==================================================
# 9. DASHBOARD VIEW
if bagian == "Overview":
    render_overview(
        df, df_asli, kolom_numerik, tampilkan_insight, jumlah_kosong
    )
elif bagian == "Chart Builder":
    render_chart_builder(df, kolom_numerik)
elif bagian == "Data Explorer":
    render_data_explorer(df, df_asli, tampilkan_tabel)
elif bagian == "Data Quality":
    render_data_quality(df)


# 13. FOOTER
# ==================================================
st.divider()

st.caption(
    "MindScope | Interactive Data Exploration Dashboard"
)

st.caption(
    "Dataset dummy bersifat sintetis. "
    "Skor tidak digunakan untuk diagnosis klinis."
)
