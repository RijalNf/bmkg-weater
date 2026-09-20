import requests
import pandas as pd
import json
import os
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account

# ============================================
# KONFIGURASI
# ============================================
GCP_PROJECT_ID = "belajar-etl-rijal"
BQ_DATASET = "weather_dataset"
BQ_TABLE = "bmkg_weather"
ADM4_CODE = "32.15.29.2003"  # Purwasari, Karawang

API_URL = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={ADM4_CODE}"


# ============================================
# EXTRACT
# ============================================
def extract():
    """Ambil data cuaca dari BMKG API."""
    print("[EXTRACT] Mengambil data dari BMKG...")
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    print(f"  Berhasil ambil data untuk {data['lokasi']['desa']}")
    return data


# ============================================
# TRANSFORM
# ============================================
def transform(raw_data):
    """Bersihkan & ubah data cuaca."""
    print("[TRANSFORM] Memproses data...")
    lokasi = raw_data['lokasi']
    rows = []
    
    for day_data in raw_data['data']:
        for time_slot in day_data['cuaca']:
            for item in time_slot:
                rows.append({
                    'provinsi': lokasi['provinsi'],
                    'kabupaten': lokasi['kotkab'],
                    'kecamatan': lokasi['kecamatan'],
                    'desa': lokasi['desa'],
                    'datetime_utc': item['utc_datetime'],
                    'datetime_local': item['local_datetime'],
                    'suhu': item['t'],
                    'kelembapan': item['hu'],
                    'cuaca': item['weather_desc'],
                    'kecepatan_angin': item['ws'],
                    'arah_angin': item['wd'],
                    'tutupan_awan': item['tcc'],
                })
    
    df = pd.DataFrame(rows)
    df['datetime_local'] = pd.to_datetime(df['datetime_local'])
    df['tanggal'] = df['datetime_local'].dt.date
    df = df.drop_duplicates(subset=['desa', 'datetime_local'])
    df = df.sort_values('datetime_local').reset_index(drop=True)
    print(f"  Setelah transform: {len(df)} baris")
    return df


# ============================================
# LOAD
# ============================================
def load(df):
    """Simpan ke BigQuery."""
    print("[LOAD] Menyimpan ke BigQuery...")
    gcp_key_json = os.environ.get('GCP_KEY')
    
    if gcp_key_json:
        credentials_info = json.loads(gcp_key_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
    else:
        credentials = service_account.Credentials.from_service_account_file('gcp_key.json')
    
    client = bigquery.Client(credentials=credentials, project=GCP_PROJECT_ID)
    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        autodetect=True,
    )
    
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"  Berhasil load {len(df)} baris ke {table_id}")


# ============================================
# RUN
# ============================================
def run_etl():
    print("=" * 40)
    print(f"ETL BMKG DIMULAI: {datetime.now()}")
    print("=" * 40)
    raw_data = extract()
    df = transform(raw_data)
    load(df)
    print("=" * 40)
    print("ETL SELESAI")
    print("=" * 40)


if __name__ == "__main__":
    run_etl()