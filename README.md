# BMKG Weather ETL

Pipeline ETL untuk mengambil data cuaca dari BMKG API dan menyimpannya ke BigQuery.

## Fitur

- Extract data cuaca dari BMKG API
- Transform data jadi format tabular
- Load ke Google BigQuery
- Scheduler otomatis tiap hari via GitHub Actions

## Lokasi

- Desa: Purwasari
- Kecamatan: Purwasari
- Kabupaten: Karawang
- Provinsi: Jawa Barat

## Cara Menjalankan

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variable `GCP_KEY` dengan isi file `gcp_key.json`
3. Jalankan: `python etl_bmkg.py`
