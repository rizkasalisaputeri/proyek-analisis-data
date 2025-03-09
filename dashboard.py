import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
day_df = pd.read_csv("data/day.csv")
hour_df = pd.read_csv("data/hour.csv")

# Mengubah kolom tanggal menjadi format datetime agar bisa difilter

day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Sidebar input untuk filter rentang waktu
# Pengguna dapat memilih rentang waktu analisis menggunakan sidebar

with st.sidebar:
    start_date, end_date = st.date_input(
        "Pilih Rentang Waktu",
        min_value=day_df["dteday"].min().date(),
        max_value=day_df["dteday"].max().date(),
        value=[day_df["dteday"].min().date(), day_df["dteday"].max().date()]
    )

# Konversi start_date dan end_date ke datetime64 agar sesuai dengan dataset

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter dataset berdasarkan rentang waktu yang dipilih
main_df = day_df[(day_df["dteday"] >= start_date) & (day_df["dteday"] <= end_date)]
main_hour_df = hour_df[(hour_df["dteday"] >= start_date) & (hour_df["dteday"] <= end_date)]

# Header utama dashboard
st.header('📊 Bike Share Dashboard')

# Menampilkan jumlah data yang masuk dalam rentang waktu yang dipilih
st.write(f"Jumlah data dalam rentang waktu ({start_date.date()} - {end_date.date()}): {len(main_hour_df)} baris")

# Jika tidak ada data dalam rentang waktu yang dipilih, tampilkan peringatan
if main_hour_df.empty:
    st.warning("⚠️ Tidak ada data dalam rentang waktu yang dipilih. Silakan pilih rentang waktu lain.")
else:
    # Visualisasi 1: Penyewaan Sepeda per Jam (Hari Kerja vs Hari Libur)
    st.subheader("Pola Penyewaan Sepeda per Jam (Hari Kerja vs Hari Libur)")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=main_hour_df[main_hour_df["workingday"] == 1],
        x="hr", y="cnt", label="Hari Kerja", ax=ax, marker="o", color="seagreen"
    )
    sns.lineplot(
        data=main_hour_df[main_hour_df["workingday"] == 0],
        x="hr", y="cnt", label="Hari Libur", ax=ax, marker="s", color="darkorange"
    )
    ax.set_title("Pola Penyewaan Sepeda per Jam", fontsize=14)
    ax.set_xlabel("Jam", fontsize=12)
    ax.set_ylabel("Total Penyewaan", fontsize=12)
    ax.legend()
    st.pyplot(fig)

    # Visualisasi 2: Pola Penyewaan Casual vs Registered Berdasarkan Jam dan Hari
    hourly_rentals = main_hour_df.groupby(["hr", "workingday"]).agg({
        "casual": "sum",
        "registered": "sum"
    }).reset_index()

    st.subheader("Pola Penyewaan Casual vs Registered Berdasarkan Jam dan Hari")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    
    sns.lineplot(ax=axes[0], x="hr", y="casual", data=hourly_rentals[hourly_rentals["workingday"] == 1],
                 label="Casual Users", color="orange", marker="o")
    sns.lineplot(ax=axes[0], x="hr", y="registered", data=hourly_rentals[hourly_rentals["workingday"] == 1],
                 label="Registered Users", color="blue", marker="o")
    axes[0].set_title("Pola Penyewaan di Hari Kerja")
    axes[0].set_xlabel("Jam (hr)")
    axes[0].set_ylabel("Jumlah Penyewaan")
    axes[0].legend()
    axes[0].grid(True)
    
    sns.lineplot(ax=axes[1], x="hr", y="casual", data=hourly_rentals[hourly_rentals["workingday"] == 0],
                 label="Casual Users", color="orange", marker="o")
    sns.lineplot(ax=axes[1], x="hr", y="registered", data=hourly_rentals[hourly_rentals["workingday"] == 0],
                 label="Registered Users", color="blue", marker="o")
    axes[1].set_title("Pola Penyewaan di Akhir Pekan/Libur")
    axes[1].set_xlabel("Jam (hr)")
    axes[1].legend()
    axes[1].grid(True)
    st.pyplot(fig)

    # Visualisasi 3: Distribusi Recency, Frequency, dan Monetary
    st.subheader("Analisis Recency, Frequency, dan Monetary (RFM)")
    
    latest_date = day_df['dteday'].max()
    day_df['Recency'] = (latest_date - day_df['dteday']).dt.days
    
    rfm_df = day_df.groupby('dteday').agg(Frequency=('cnt', 'count')).reset_index()
    rfm_df['Monetary'] = day_df.groupby('dteday')['cnt'].sum().values
    rfm_df = rfm_df.merge(day_df[['dteday', 'Recency']], on='dteday', how='left')
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    axes[0].hist(rfm_df['Recency'], bins=20, color='blue', alpha=0.7, edgecolor='black')
    axes[0].set_title('Distribution of Recency')
    
    axes[1].hist(rfm_df['Frequency'], bins=10, color='orange', alpha=0.7, edgecolor='black')
    axes[1].set_title('Distribution of Frequency')
    
    axes[2].hist(rfm_df['Monetary'], bins=20, color='green', alpha=0.7, edgecolor='black')
    axes[2].set_title('Distribution of Monetary Value')
    st.pyplot(fig)

st.caption('© 2024 Bike Share Analytics. All Rights Reserved.')
