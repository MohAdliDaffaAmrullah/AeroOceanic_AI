import xarray as xr
import numpy as np
import pandas as pd
import datetime

print("🚀 Bot GitHub Actions mulai mengolah data hidrodinamika otomatis...")

# 1. Membuat koordinat grid laut buatan untuk wilayah simulasi
latitudes = np.linspace(-6.2, -5.8, 40)   
longitudes = np.linspace(106.6, 107.1, 40) 
# Waktu otomatis mengikuti hari ini saat bot berjalan di server
hari_ini = datetime.date.today().strftime("%Y-%m-%d")
times = pd.date_range(start=hari_ini, periods=24, freq="H") 

# 2. Rumus Fisika Arus Pasang Surut buatan
current_data = np.zeros((len(times), len(latitudes), len(longitudes)))
for t in range(len(times)):
    current_data[t, :, :] = np.sin(t * 0.2) * np.outer(np.cos(latitudes * 10), np.sin(longitudes * 10))

# 3. Masukkan ke struktur data geospasial NetCDF
ds = xr.Dataset(
    {
        "surface_current": (["time", "lat", "lon"], current_data, {"units": "m/s"})
    },
    coords={"time": times, "lat": latitudes, "lon": longitudes}
)

# 4. Simpan menjadi file utama
ds.to_netcdf("data_laut.nc")
print("✅ Pembaruan data_laut.nc sukses! Server siap menyinkronkan ke dashboard.")
