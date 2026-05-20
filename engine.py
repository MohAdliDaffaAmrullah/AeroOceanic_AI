import numpy as np
import xarray as xr
import pandas as pd
import datetime
import requests
import os

print("=== AEROOCEANIC AI: ADVANCED FORCED HYDRODYNAMICS ENGINE ===")

# 1. Koordinat Proyek (Pesisir Cisadane - Teluk Jakarta)
lat_center, lon_center = -5.95, 106.85
lat = np.linspace(-6.20, -5.80, 40)
lon = np.linspace(106.60, 107.10, 40)

# 2. Setup Waktu Operasional (Hari Ini)
start_date = datetime.datetime(2026, 5, 20, 0, 0, 0)
time_array = pd.date_range(start=start_date, periods=24, freq="h")

# 3. ASIMILASI DATA REAL-TIME: Ambil data Angin Aktual via API Cuaca Global
print("Mengunduh data angin aktual permukaan dari satelit...")
url = f"https://api.open-meteo.com/v1/forecast?latitude={lat_center}&longitude={lon_center}&hourly=wind_speed_10m,wind_direction_10m&timezone=Asia%2FJakarta&start_date=2026-05-20&end_date=2026-05-20"

try:
    response = requests.get(url).json()
    w_speed = np.array(response['hourly']['wind_speed_10m']) / 3.6 # Konversi km/jam ke m/s
    w_dir = np.array(response['hourly']['wind_direction_10m'])
    print("Sukses mengasimilasi data angin satelit!")
except Exception as e:
    print("Koneksi API gagal, menggunakan fallback angin muson barat-laut...")
    w_speed = np.full(24, 5.0) # Fallback 5 m/s
    w_dir = np.full(24, 315.0) # Dari Barat Laut

# Konversi arah angin ke komponen vektor U_wind dan V_wind (Metode Oseanografi)
wind_rad = np.radians(270 - w_dir)
U_wind = w_speed * np.cos(wind_rad)
V_wind = w_speed * np.sin(wind_rad)

# 4. Modul Pasang Surut Hidrodinamika (Komponen Harmonik M2 & K1)
A_M2, omega_M2, g_M2 = 0.28, 28.984, 110.0
A_K1, omega_K1, g_K1 = 0.18, 15.041, 230.0

# 5. Simulasi Ruang dan Waktu 2D (Looping Numerik)
U_current = np.zeros((24, 40, 40))
V_current = np.zeros((24, 40, 40))
CD = 0.0012  # Koefisien Hambat Angin di Permukaan Air Laut

spatial_gradient = np.linspace(0.5, 1.3, 40)

for t in range(24):
    # Hitung kecepatan arus akibat pasut (Osilasi)
    u_tide = A_M2 * np.cos(np.radians(omega_M2 * t - g_M2)) + A_K1 * np.cos(np.radians(omega_K1 * t - g_K1))
    v_tide = A_M2 * np.sin(np.radians(omega_M2 * t - g_M2)) * 0.5 # Polarisasi elips
    
    # Hitung kontribusi arus akibat seretan angin permukaan (Wind-Driven Current)
    u_wind_driven = CD * U_wind[t] * np.abs(U_wind[t])
    v_wind_driven = CD * V_wind[t] * np.abs(V_wind[t])
    
    for i in range(40):
        # Gabungkan gaya Pasut + Angin + Efek Batimetri Pesisir Pantai
        U_current[t, i, :] = (u_tide + u_wind_driven) * spatial_gradient[i]
        V_current[t, i, :] = (v_tide + v_wind_driven) * spatial_gradient[i]

# Hitung Magnitudo Total Kecepatan Arul (Skalar Selalu Positif)
speed = np.sqrt(U_current**2 + V_current**2)

# 6. Kemas ke NetCDF Multi-Variabel Standar COARDS/CF
ds = xr.Dataset(
    data_vars={
        "surface_current": (["time", "lat", "lon"], speed, {"units": "m/s", "long_name": "Current Speed Magnitude"}),
        "u_current": (["time", "lat", "lon"], U_current, {"units": "m/s", "long_name": "Zonal Velocity Component (U)"}),
        "v_current": (["time", "lat", "lon"], V_current, {"units": "m/s", "long_name": "Meridional Velocity Component (V)"})
    },
    coords={
        "time": time_array,
        "lat": (["lat"], lat, {"units": "degrees_north"}),
        "lon": (["lon"], lon, {"units": "degrees_east"})
    }
)

if os.path.exists("data_laut.nc"): os.remove("data_laut.nc")
ds.to_netcdf("data_laut.nc")
print("PROSES SELESAI: Model 2D Komponen Vektor berhasil diciptakan!")
