import numpy as np
import pandas as pd
import streamlit as st


# Generate a stable synthetic dataset for demos and development.
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
