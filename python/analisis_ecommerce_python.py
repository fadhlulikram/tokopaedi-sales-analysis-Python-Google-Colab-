```python:Kode Analisis Python:analisis_ecommerce_python.py
# ==============================================================================
# TOKOPAEDI SALES ANALYSIS - PYTHON (GOOGLE COLAB)
# Nama: Fadhlul Ikram
# Dataset: order_detail, sku_detail, customer_detail, payment_detail
# ==============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Mengatur format tampilan angka desimal di pandas
pd.options.display.float_format = lambda x: f"{x:,.0f}".replace(',', '.')

# ------------------------------------------------------------------------------
# PERSIAPAN DATA (LOAD DATASET DARI GITHUB REPOSITORY)
# ------------------------------------------------------------------------------
path_od = "https://raw.githubusercontent.com/fadhlulikram/tokopaedi-sales-analysis-Python-Google-Colab-/refs/heads/main/dataset/order_detail.csv"
path_pd = "https://raw.githubusercontent.com/fadhlulikram/tokopaedi-sales-analysis-Python-Google-Colab-/refs/heads/main/dataset/payment_detail.csv"
path_cd = "https://raw.githubusercontent.com/fadhlulikram/tokopaedi-sales-analysis-Python-Google-Colab-/refs/heads/main/dataset/customer_detail.csv"
path_sd = "https://raw.githubusercontent.com/fadhlulikram/tokopaedi-sales-analysis-Python-Google-Colab-/refs/heads/main/dataset/sku_detail.csv"

df_od = pd.read_csv(path_od)
df_pd = pd.read_csv(path_pd)
df_cd = pd.read_csv(path_cd)
df_sd = pd.read_csv(path_sd)

# Ubah kolom tanggal dari teks (object) menjadi tipe datetime
df_od['order_date'] = pd.to_datetime(df_od['order_date'])
df_cd['registered_date'] = pd.to_datetime(df_cd['registered_date'])


# ==============================================================================
# SOAL 1: Top 5 Produk Kategori Mobiles & Tablets Tahun 2022
# ==============================================================================
# Gabungkan tabel order_detail dan sku_detail
df_od_sd = pd.merge(
    df_od, 
    df_sd, 
    left_on='sku_id', 
    right_on='id', 
    suffixes=('', '_sku')
)

# Filter khusus kategori Mobiles & Tablets di tahun 2022 yang sudah dibayar (is_valid = 1)
filtered_soal1 = df_od_sd[
    (df_od_sd['category'] == 'Mobiles & Tablets') &
    (df_od_sd['order_date'].dt.year == 2022) &
    (df_od_sd['is_valid'] == 1)
]

# Hitung total barang terjual per produk dan ambil 5 teratas
top5_mobiles = (
    filtered_soal1.groupby(['sku_id', 'sku_name'])['qty_ordered']
    .sum()
    .reset_index()
    .sort_values('qty_ordered', ascending=False)
    .head(5)
    .reset_index(drop=True)
)
print("=== Top 5 Produk Mobiles & Tablets (2022) ===")
print(top5_mobiles)

# Buat grafik horizontal bar chart (urutkan dari bawah ke atas supaya yang terbesar di atas)
top5_plot = top5_mobiles.sort_values('qty_ordered', ascending=True)
top5_plot.plot(
    x='sku_name',
    y='qty_ordered',
    kind='barh',
    xlabel='Total Qty Sold',
    ylabel='Product Name',
    figsize=(10, 6),
    title='Top 5 Products - Mobiles & Tablets (2022)',
    legend=False
)
plt.tight_layout()
plt.show()


# ==============================================================================
# SOAL 2.1: Perbandingan Penjualan 15 Kategori (2021 vs 2022)
# ==============================================================================
# Tambahkan kolom tahun untuk memudahkan filter
df_od['tahun'] = df_od['order_date'].dt.year
merged_soal2 = df_od.merge(df_sd, left_on='sku_id', right_on='id', suffixes=('_order', '_sku'))

# Ambil transaksi yang sudah dibayar saja
valid_orders = merged_soal2[merged_soal2['is_valid'] == 1]

# Jumlahkan qty_ordered per kategori untuk masing-masing tahun
qty_2021 = valid_orders[valid_orders['tahun'] == 2021].groupby('category')['qty_ordered'].sum().reset_index().rename(columns={'qty_ordered': 'qty_2021'})
qty_2022 = valid_orders[valid_orders['tahun'] == 2022].groupby('category')['qty_ordered'].sum().reset_index().rename(columns={'qty_ordered': 'qty_2022'})

# Gabungkan data 2021 dan 2022 lalu hitung selisihnya
cat_compare = qty_2021.merge(qty_2022, on='category', how='outer').fillna(0)
cat_compare['qty_2021'] = cat_compare['qty_2021'].astype(int)
cat_compare['qty_2022'] = cat_compare['qty_2022'].astype(int)
cat_compare['selisih'] = cat_compare['qty_2022'] - cat_compare['qty_2021']
cat_compare = cat_compare.sort_values('selisih').reset_index(drop=True)

print("\n=== Perbandingan Qty Terjual per Kategori (2021 vs 2022) ===")
print(cat_compare)

# Visualisasi selisih per kategori (merah jika turun, hijau jika naik)
colors = ['#EA4335' if v < 0 else '#34A853' for v in cat_compare['selisih']]
fig, ax = plt.subplots(figsize=(10, 8))
bars = ax.barh(cat_compare['category'], cat_compare['selisih'], color=colors)

for bar, v in zip(bars, cat_compare['selisih']):
    x = bar.get_width()
    align = 'left' if v >= 0 else 'right'
    offset = 15 if v >= 0 else -15
    ax.text(x + offset, bar.get_y() + bar.get_height()/2, f'{v:+,}', va='center', ha=align, fontsize=9)

ax.axvline(0, color='black', linewidth=0.8)
ax.set_title('Selisih Qty Ordered per Kategori (2022 vs 2021)', fontsize=14, fontweight='bold')
ax.set_xlabel('Selisih Qty Ordered')
plt.tight_layout()
plt.show()


# ==============================================================================
# SOAL 2.2: Top 20 Produk yang Paling Turun di Kategori Others (2022 vs 2021)
# ==============================================================================
others_valid = valid_orders[valid_orders['category'] == 'Others']

others_2021 = others_valid[others_valid['tahun'] == 2021].groupby('sku_name')['qty_ordered'].sum().reset_index().rename(columns={'qty_ordered': 'qty_2021'})
others_2022 = others_valid[others_valid['tahun'] == 2022].groupby('sku_name')['qty_ordered'].sum().reset_index().rename(columns={'qty_ordered': 'qty_2022'})

compare_others = others_2021.merge(others_2022, on='sku_name', how='outer').fillna(0)
compare_others['qty_2021'] = compare_others['qty_2021'].astype(int)
compare_others['qty_2022'] = compare_others['qty_2022'].astype(int)
compare_others['selisih'] = compare_others['qty_2022'] - compare_others['qty_2021']

# Urutkan dari yang penurunannya paling besar dan ambil 20 teratas
top20_turun = compare_others.sort_values('selisih').head(20).reset_index(drop=True)
print("\n=== Top 20 Produk Penurunan Terbesar di Kategori Others ===")
print(top20_turun)


# ==============================================================================
# SOAL 3: Pelanggan yang Checkout Tapi Belum Bayar di Tahun 2022
# ==============================================================================
# Gabungkan order_detail dengan customer_detail untuk mengambil tanggal registrasi
df_od_cd = pd.merge(df_od, df_cd, left_on='customer_id', right_on='id')

# Filter transaksi tahun 2022 yang berstatus gross=1, valid=0, net=0
belum_bayar_2022 = df_od_cd[
    (df_od_cd['is_gross'] == 1) &
    (df_od_cd['is_valid'] == 0) &
    (df_od_cd['is_net'] == 0) &
    (df_od_cd['order_date'].dt.year == 2022)
][['customer_id', 'registered_date']].drop_duplicates().sort_values('registered_date', ascending=False).reset_index(drop=True)

print("\n=== Data Pelanggan Checkout Belum Bayar (2022) ===")
print(belum_bayar_2022)


# ==============================================================================
# SOAL 4.1 & 4.2: Rata-rata Penjualan Harian Weekend vs Weekday (Okt-Des 2022)
# ==============================================================================
# Buat kolom nama hari dan nama bulan
df_od['day'] = df_od['order_date'].dt.day_name()
df_od['month'] = df_od['order_date'].dt.month_name()

# Filter transaksi valid dan tandai apakah termasuk Weekend atau Weekday
df_valid = df_od[df_od['is_valid'] == 1].copy()
df_valid['day_type'] = df_valid['day'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday')

# Ambil periode campaign Oktober sampai Desember 2022
campaign_period = df_valid[(df_valid['order_date'] >= '2022-10-01') & (df_valid['order_date'] <= '2022-12-31')]

# Jumlahkan dulu total penjualan (before_discount) per tanggal
daily_sum = (
    campaign_period
    .groupby(['month', 'day_type', campaign_period['order_date'].dt.date])['before_discount']
    .sum()
    .reset_index()
)

# Soal 4.1: Hitung rata-rata harian per bulan untuk Weekday vs Weekend
avg_per_month_daytype = (
    daily_sum
    .groupby(['month', 'day_type'])['before_discount']
    .mean()
    .unstack('day_type')
    .reindex(['October', 'November', 'December'])
    .reset_index()
    .assign(selisih=lambda d: d['Weekend'] - d['Weekday'])
    .assign(persen=lambda d: (d['selisih'] / d['Weekday'] * 100).round(2))
)
print("\n=== Rata-rata Harian Weekday vs Weekend per Bulan (Okt-Des 2022) ===")
print(avg_per_month_daytype)

# Grafik perbandingan per bulan
avg_per_month_daytype.set_index('month')[['Weekday', 'Weekend']].plot(
    kind='bar', figsize=(8, 5), title='Rata-rata Penjualan Harian: Weekday vs Weekend (Okt-Des 2022)'
)
plt.ylabel('Rata-rata before_discount')
plt.xlabel('Bulan')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# Soal 4.2: Hitung rata-rata harian gabungan selama 3 bulan penuh
rata2_weekends = daily_sum[daily_sum['day_type'] == 'Weekend']['before_discount'].mean()
rata2_weekdays = daily_sum[daily_sum['day_type'] == 'Weekday']['before_discount'].mean()

rekap_3_bulan = pd.DataFrame({
    'Periode': ['Total 3 Bulan (Okt-Des 2022)'],
    'AVG Weekends': [rata2_weekends],
    'AVG Weekdays': [rata2_weekdays],
    'Selisih (%)': [f"{(rata2_weekends - rata2_weekdays) / rata2_weekdays * 100:.2f}%"]
})
print("\n=== Rata-rata Harian Weekday vs Weekend Total 3 Bulan ===")
print(rekap_3_bulan)

