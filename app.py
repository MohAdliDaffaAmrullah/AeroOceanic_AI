import streamlit as st
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="AeroOceanic AI - Hydrodynamics Portal", layout="wide")
st.title("🌊 AeroOceanic AI: Real-Time Dynamic Current & Wind Vector Dashboard")
st.write("Lokasi Analisis: Pesisir Cisadane - Teluk Jakarta (Operasional Otomatis)")

@st.cache_data(ttl=3600)
def load_data():
    return xr.open_dataset("data_laut.nc")

try:
    ds = load_data()
    st.sidebar.header("Parameter Kontrol")
    time_list = [str(t)[:19] for t in ds.time.values]
    selected_time_str = st.sidebar.selectbox("Pilih Waktu Analisis (WIB)", time_list)
    
    selected_ds = ds.sel(time=selected_time_str)
    lat = selected_ds.lat.values
    lon = selected_ds.lon.values
    speed = selected_ds.surface_current.values
    u = selected_ds.u_current.values
    v = selected_ds.v_current.values
    
    fig, ax = plt.subplots(figsize=(11, 7))
    contour = ax.contourf(lon, lat, speed, levels=25, cmap="jet")
    cbar = fig.colorbar(contour, ax=ax)
    cbar.set_label("Total Current Speed Magnitude [m/s]", fontsize=12)
    
    skip = 2
    ax.quiver(lon[::skip], lat[::skip], u[::skip, ::skip], v[::skip, ::skip],
              color="white", scale=5.0, width=0.003, edgecolor="black", linewidth=0.5)
    
    ax.set_title(f"Vektor Arah dan Magnitudo Arus Laut Permukaan\nTimestamp: {selected_time_str}", fontsize=13, fontweight='bold')
    ax.set_xlabel("Longitude [degrees_east]", fontsize=10)
    ax.set_ylabel("Latitude [degrees_north]", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.pyplot(fig)
    with col2:
        st.metric(label="Kecepatan Arus Maksimum", value=f"{np.max(speed):.3f} m/s")
        st.metric(label="Rata-rata Kecepatan", value=f"{np.mean(speed):.3f} m/s")
        st.write("Panah putih menunjukkan **arah aliran air secara spasial** akibat kombinasi pasut dan angin satelit.")
except Exception as e:
    st.error(f"Gagal memuat visualisasi. Error: {e}")
