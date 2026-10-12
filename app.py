
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==================================================
# 1. KONFIGURASI DAN TAMPILAN
# ==================================================
st.set_page_config(
    page_title="MindScope | Mental Health Dashboard",
    page_icon="🧠",
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
    background: linear-gradient(180deg, #151D3B, #29366B);
}
[data-testid="stSidebar"] * {
    color: #FFFFFF;
}
.block-container {
    padding-top: 1.8rem;
    max-width: 1500px;
}
.hero {
    background: linear-gradient(120deg, #172044, #414CC5, #6966E8);
    padding: 30px;
    border-radius: 22px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(49, 61, 150, .15);
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
    border-radius: 16px;
    padding: 17px;
    box-shadow: 0 4px 16px rgba(25, 39, 85, .04);
}
div[data-testid="stMetricLabel"] {
    color: #6B7590;
}
div[data-testid="stMetricValue"] {
    color: #20294B;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# 2. DATASET DUMMY
# ==================================================
@st.cache_data
def buat_data_dummy():
    rng = np.random.default_rng(42)
    n = 120

    usia = rng.integers(18, 61, n)
    tidur = np.clip(rng.normal(6.8, 1.2, n), 3, 10).round(1)
    aktivitas = rng.integers(0, 8, n)
    kerja = np.clip(rng.normal(7.2, 2, n), 1, 14).round(1)

    dukungan = rng.choice(
        ["Rendah", "Sedang", "Tinggi"],
        n,
        p=[0.2, 0.5, 0.3]
    )

    stres = np.clip(
        np.rint(
            5 + (kerja - 7) * 0.65
            + (6.5 - tidur) * 0.8
            - aktivitas * 0.25
            + rng.normal(0, 1.8, n)
        ), 0, 10
    ).astype(int)

    cemas = np.clip(
        np.rint(
            stres * 0.65
            + (6.5 - tidur) * 0.5
            + rng.normal(0, 2, n)
        ), 0, 10
    ).astype(int)

    depresi = np.clip(
        np.rint(
            (6.5 - tidur) * 0.75
            + (5 - aktivitas) * 0.35
            + (dukungan == "Rendah") * 1.5
            + rng.normal(2.5, 1.8, n)
        ), 0, 10
    ).astype(int)

    def kategori(skor):
        if skor <= 3:
            return "Rendah"
        elif skor <= 6:
            return "Sedang"
        return "Tinggi"

    df = pd.DataFrame({
        "responden_id": [f"R{i:03}" for i in range(1, n + 1)],
        "usia": usia,
        "jenis_kelamin": rng.choice(
            ["Laki-laki", "Perempuan"], n
        ),
        "pekerjaan": rng.choice(
            ["Mahasiswa", "Karyawan", "Wiraswasta",
             "Pencari Kerja", "Lainnya"],
            n
        ),
        "jam_tidur_per_hari": tidur,
        "jam_kerja_belajar_per_hari": kerja,
        "aktivitas_fisik_hari_per_minggu": aktivitas,
        "dukungan_sosial": dukungan,
        "skor_stres_0_10": stres,
        "skor_kecemasan_0_10": cemas,
        "skor_depresi_0_10": depresi
    })

    for nama, skor in [
        ("stres", stres),
        ("kecemasan", cemas),
        ("depresi", depresi)
    ]:
        df[f"kategori_{nama}"] = [
            kategori(int(x)) for x in skor
        ]

    return df


# ==================================================
# 3. HEADER DASHBOARD
# ==================================================
st.markdown("""
<div class="hero">
    <p>DATA EXPLORATION STUDIO</p>
    <h1>🧠 MindScope</h1>
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
    st.title("🧭 Control Center")
    st.caption("Atur sumber data dan preferensi analisis.")

    sumber = st.radio(
        "Sumber Dataset",
        ["Dataset Demo", "Upload CSV Sendiri"]
    )

    file_csv = None

    if sumber == "Upload CSV Sendiri":
        file_csv = st.file_uploader(
            "Upload file CSV",
            type=["csv"]
        )

    st.divider()

    st.subheader("⚙️ Pengaturan")
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
    df_asli = buat_data_dummy()

else:
    if file_csv is None:
        st.info(
            "⬅️ Upload file CSV melalui sidebar "
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
    '<p class="section-title">🎚️ Filter Data</p>',
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

with st.expander("➕ Filter numerik"):
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
    '<p class="section-title">📌 Ringkasan Dataset</p>',
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
# 8. NAVIGASI DASHBOARD
# ==================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "✨ Overview",
    "📊 Chart Builder",
    "🧾 Data Explorer",
    "🧹 Data Quality"
])


# ==================================================
# 9. OVERVIEW
# ==================================================
with tab1:
    kiri, kanan = st.columns(2)

    with kiri:
        st.subheader("Komposisi Kategori")

        kategori_tersedia = [
            c for c in df.columns
            if c not in kolom_numerik
        ]

        if kategori_tersedia:
            default_kategori = next(
                (
                    c for c in kategori_tersedia
                    if any(k in c.lower() for k in [
                        "kategori_stres", "pekerjaan",
                        "jenis_kelamin", "dukungan"
                    ])
                ),
                kategori_tersedia[0]
            )

            pilih_kategori = st.selectbox(
                "Pilih variabel kategori",
                kategori_tersedia,
                index=kategori_tersedia.index(
                    default_kategori
                ),
                key="overview_kategori"
            )

            hitung = (
                df[ pilih_kategori ]
                .fillna("(Kosong)")
                .astype(str)
                .value_counts()
                .head(15)
                .rename_axis("Kategori")
                .reset_index(name="Jumlah")
            )

            fig = px.pie(
                hitung,
                names="Kategori",
                values="Jumlah",
                hole=0.5,
                title="Distribusi Kategori",
                color_discrete_sequence=(
                    px.colors.qualitative.Bold
                )
            )

            fig.update_traces(
                textinfo="percent+label"
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(
                fig, use_container_width=True
            )
        else:
            st.info("Tidak ada kolom kategori.")

    with kanan:
        st.subheader("Distribusi Numerik")

        if kolom_numerik:
            pilih_angka = st.selectbox(
                "Pilih variabel numerik",
                kolom_numerik,
                key="overview_numerik"
            )

            fig = px.histogram(
                df,
                x=pilih_angka,
                nbins=20,
                marginal="box",
                title=f"Distribusi {pilih_angka}",
                color_discrete_sequence=["#5965DC"]
            )

            fig.update_layout(template="plotly_white")
            st.plotly_chart(
                fig, use_container_width=True
            )
        else:
            st.info("Tidak ada kolom numerik.")

    if tampilkan_insight:
        st.subheader("💡 Ringkasan Otomatis")

        st.write(
            f"- Data yang sedang dianalisis memiliki "
            f"**{len(df)} baris** dari total "
            f"**{len(df_asli)} baris**."
        )

        st.write(
            f"- Terdapat **{df.shape[1]} variabel** "
            f"dan **{jumlah_kosong} sel kosong**."
        )

        if kolom_numerik:
            rata_rata = df[kolom_numerik].mean(
                numeric_only=True
            ).dropna()

            if not rata_rata.empty:
                c_tertinggi = rata_rata.idxmax()
                st.write(
                    f"- Rata-rata numerik terbesar: "
                    f"**{c_tertinggi}** "
                    f"({rata_rata[c_tertinggi]:.2f})."
                )

        st.caption(
            "Ringkasan bersifat deskriptif, "
            "bukan diagnosis atau bukti sebab-akibat."
        )


# ==================================================
# 10. CHART BUILDER
# ==================================================
with tab2:
    st.subheader("🛠️ Bangun Grafik Sendiri")

    st.caption(
        "Ubah pilihan untuk memperbarui grafik secara otomatis."
    )

    jenis_grafik = st.selectbox(
        "Jenis Grafik",
        [
            "Bar Chart",
            "Line Chart",
            "Scatter Plot",
            "Histogram",
            "Box Plot",
            "Violin Plot",
            "Pie / Donut",
            "Area Chart",
            "Heatmap Korelasi"
        ]
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        kolom_x = st.selectbox(
            "Variabel X / Kategori",
            df.columns.tolist()
        )

    with c2:
        pilihan_y = (
            kolom_numerik
            if kolom_numerik
            else df.columns.tolist()
        )

        kolom_y = st.selectbox(
            "Variabel Y / Nilai",
            pilihan_y
        )

    with c3:
        pilihan_warna = ["Tidak Ada"] + df.columns.tolist()

        warna = st.selectbox(
            "Warna / Kelompok",
            pilihan_warna
        )

    c4, c5 = st.columns(2)

    with c4:
        agregasi = st.selectbox(
            "Metode Agregasi",
            [
                "Rata-rata",
                "Jumlah",
                "Total",
                "Minimum",
                "Maksimum",
                "Median"
            ]
        )

    with c5:
        judul = st.text_input(
            "Judul Grafik",
            value=f"{jenis_grafik}: {kolom_y}"
        )

    c6, c7 = st.columns(2)

    with c6:
        jumlah_kategori = st.slider(
            "Maksimum kategori",
            min_value=5,
            max_value=30,
            value=15
        )

    with c7:
        tampilkan_label = st.toggle(
            "Tampilkan label nilai",
            value=True
        )

    warna_arg = None if warna == "Tidak Ada" else warna

    try:
        if jenis_grafik == "Heatmap Korelasi":
            if len(kolom_numerik) < 2:
                st.warning(
                    "Heatmap memerlukan minimal "
                    "dua kolom numerik."
                )
            else:
                korelasi = df[kolom_numerik].corr(
                    numeric_only=True
                )

                fig = px.imshow(
                    korelasi,
                    text_auto=".2f",
                    aspect="auto",
                    color_continuous_scale="RdBu_r",
                    zmin=-1,
                    zmax=1,
                    title=judul
                )

                fig.update_layout(template="plotly_white")
                st.plotly_chart(
                    fig, use_container_width=True
                )

                st.caption(
                    "Korelasi bukan bukti sebab-akibat."
                )

        elif jenis_grafik == "Histogram":
            fig = px.histogram(
                df,
                x=kolom_y,
                color=warna_arg,
                nbins=jumlah_kategori,
                title=judul
            )

            fig.update_layout(template="plotly_white")
            st.plotly_chart(
                fig, use_container_width=True
            )

        elif jenis_grafik in ["Box Plot", "Violin Plot"]:
            if kolom_y not in kolom_numerik:
                st.warning(
                    "Pilih variabel Y yang numerik."
                )
            else:
                if jenis_grafik == "Box Plot":
                    fig = px.box(
                        df,
                        x=kolom_x if kolom_x != kolom_y else None,
                        y=kolom_y,
                        color=warna_arg,
                        title=judul,
                        points="outliers"
                    )
                else:
                    fig = px.violin(
                        df,
                        x=kolom_x if kolom_x != kolom_y else None,
                        y=kolom_y,
                        color=warna_arg,
                        box=True,
                        points="outliers",
                        title=judul
                    )

                fig.update_layout(template="plotly_white")
                st.plotly_chart(
                    fig, use_container_width=True
                )

        elif jenis_grafik == "Pie / Donut":
            hitung = (
                df[kolom_x]
                .fillna("(Kosong)")
                .astype(str)
                .value_counts()
                .head(jumlah_kategori)
                .rename_axis("Kategori")
                .reset_index(name="Jumlah")
            )

            fig = px.pie(
                hitung,
                names="Kategori",
                values="Jumlah",
                hole=0.45,
                title=judul
            )

            if tampilkan_label:
                fig.update_traces(
                    textinfo="percent+label"
                )

            fig.update_layout(template="plotly_white")
            st.plotly_chart(
                fig, use_container_width=True
            )

        elif jenis_grafik == "Scatter Plot":
            if (
                kolom_x not in kolom_numerik
                or kolom_y not in kolom_numerik
            ):
                st.warning(
                    "Scatter Plot memerlukan "
                    "variabel X dan Y numerik."
                )
            else:
                fig = px.scatter(
                    df,
                    x=kolom_x,
                    y=kolom_y,
                    color=warna_arg,
                    hover_data=df.columns.tolist(),
                    title=judul
                )

                fig.update_layout(template="plotly_white")
                st.plotly_chart(
                    fig, use_container_width=True
                )

        else:
            kerja = df.copy()
            kerja[kolom_x] = (
                kerja[kolom_x]
                .fillna("(Kosong)")
                .astype(str)
            )

            if agregasi == "Jumlah":
                ringkasan = (
                    kerja.groupby(kolom_x)
                    .size()
                    .reset_index(name="Nilai")
                )
            else:
                kerja["_nilai"] = pd.to_numeric(
                    kerja[kolom_y], errors="coerce"
                )

                grup = kerja.groupby(kolom_x)["_nilai"]

                if agregasi == "Total":
                    hasil = grup.sum(min_count=1)
                elif agregasi == "Minimum":
                    hasil = grup.min()
                elif agregasi == "Maksimum":
                    hasil = grup.max()
                elif agregasi == "Median":
                    hasil = grup.median()
                else:
                    hasil = grup.mean()

                ringkasan = hasil.reset_index(
                    name="Nilai"
                )

            ringkasan = (
                ringkasan
                .dropna(subset=["Nilai"])
                .head(jumlah_kategori)
            )

            if jenis_grafik == "Line Chart":
                fig = px.line(
                    ringkasan,
                    x=kolom_x,
                    y="Nilai",
                    markers=True,
                    title=judul
                )

            elif jenis_grafik == "Area Chart":
                fig = px.area(
                    ringkasan,
                    x=kolom_x,
                    y="Nilai",
                    title=judul
                )

            else:
                fig = px.bar(
                    ringkasan,
                    x=kolom_x,
                    y="Nilai",
                    color=warna_arg if warna_arg else kolom_x,
                    text="Nilai" if tampilkan_label else None,
                    title=judul,
                    color_discrete_sequence=(
                        px.colors.qualitative.Bold
                    )
                )

            if tampilkan_label:
                fig.update_traces(
                    texttemplate="%{y:.2f}",
                    textposition="outside"
                )

            fig.update_layout(template="plotly_white")
            st.plotly_chart(
                fig, use_container_width=True
            )

    except Exception as e:
        st.error(
            f"Grafik gagal dibuat: {e}"
        )

    with st.expander("Lihat data sumber grafik"):
        st.dataframe(df, use_container_width=True)


# ==================================================
# 11. DATA EXPLORER
# ==================================================
with tab3:
    st.subheader("🧾 Data Explorer")

    st.info(
        "Kau bisa mengedit sel, menambah baris, "
        "atau menghapus baris. Unduh CSV untuk "
        "menyimpan hasilnya. File sumber tidak "
        "akan ditimpa otomatis."
    )

    data_edit = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        height=450,
        key="editor_data"
    )

    csv_edit = data_edit.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "⬇️ Unduh Data Hasil Edit",
        data=csv_edit,
        file_name="mental_health_data_edited.csv",
        mime="text/csv"
    )

    st.download_button(
        "⬇️ Unduh Dataset Penuh",
        data=df_asli.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="mental_health_dataset.csv",
        mime="text/csv"
    )

    if tampilkan_tabel:
        st.subheader("Pratinjau Data")
        st.dataframe(
            df.head(100),
            use_container_width=True
        )


# ==================================================
# 12. DATA QUALITY
# ==================================================
with tab4:
    st.subheader("🧹 Pemeriksaan Kualitas Data")

    q1, q2, q3 = st.columns(3)

    q1.metric(
        "Baris Duplikat",
        f"{df.duplicated().sum():,}"
    )

    q2.metric(
        "Kolom Memiliki Data Kosong",
        f"{(df.isna().sum() > 0).sum():,}"
    )

    persentase_kosong = (
        df.isna().sum().sum()
        / max(df.size, 1)
        * 100
    )

    q3.metric(
        "Persentase Sel Kosong",
        f"{persentase_kosong:.2f}%"
    )

    kualitas = pd.DataFrame({
        "Kolom": df.columns,
        "Tipe Data": [
            str(df[c].dtype) for c in df.columns
        ],
        "Nilai Kosong": [
            int(df[c].isna().sum())
            for c in df.columns
        ],
        "Persentase Kosong (%)": [
            round(float(df[c].isna().mean() * 100), 2)
            for c in df.columns
        ],
        "Nilai Unik": [
            int(df[c].nunique(dropna=True))
            for c in df.columns
        ]
    })

    st.dataframe(
        kualitas,
        use_container_width=True
    )

    tipe = (
        df.dtypes.astype(str)
        .value_counts()
        .rename_axis("Tipe Data")
        .reset_index(name="Jumlah Kolom")
    )

    fig = px.bar(
        tipe,
        x="Tipe Data",
        y="Jumlah Kolom",
        color="Tipe Data",
        text="Jumlah Kolom",
        title="Distribusi Tipe Data"
    )

    fig.update_layout(template="plotly_white")
    st.plotly_chart(
        fig, use_container_width=True
    )


# ==================================================
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
