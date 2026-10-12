import pandas as pd
import plotly.express as px
import streamlit as st


def render_overview(
    df: pd.DataFrame,
    df_asli: pd.DataFrame,
    kolom_numerik: list[str],
    tampilkan_insight: bool,
    jumlah_kosong: int,
) -> None:
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
        st.subheader("Ringkasan Otomatis")

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


def render_chart_builder(
    df: pd.DataFrame,
    kolom_numerik: list[str],
) -> None:
    st.subheader("Bangun Grafik Sendiri")

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


def render_data_explorer(
    df: pd.DataFrame,
    df_asli: pd.DataFrame,
    tampilkan_tabel: bool,
) -> None:
    st.subheader("Data Explorer")

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
        "Unduh Data Hasil Edit",
        data=csv_edit,
        file_name="mental_health_data_edited.csv",
        mime="text/csv"
    )

    st.download_button(
        "Unduh Dataset Penuh",
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


def render_data_quality(df: pd.DataFrame) -> None:
    st.subheader("Pemeriksaan Kualitas Data")

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
