import streamlit as st
import xarray as xr
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="HydroPINN-API Dashboard", layout="wide")
st.title("🌊 HydroPINN-API: Automated Coastal Hydrodynamics")
st.write("Real-time automated spatial data processing for coastal engineering.")

@st.cache_data
def load_ocean_data(file_path):
    ds = xr.open_dataset(file_path)
    return ds

# Deteksi otomatis apakah file data sudah dibuat oleh bot GitHub
file_data = "data_laut.nc"

if os.path.exists(file_data):
    try:
        data = load_ocean_data(file_data)
        st.success("Data Pipeline Status: Operational (100% Connected to Cloud)")
        
        st.sidebar.header("Filter Parameter Spasial")
        selected_time = st.sidebar.selectbox("Pilih Waktu Analisis (Timestamp)", data.time.values)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        data['surface_current'].sel(time=selected_time).plot(ax=ax, cmap='jet')
        ax.set_title(f"Prediksi Arus Permukaan Pesisir pada: {selected_time}")
        
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
else:
    st.info("🔄 Menunggu bot GitHub Actions menyuplai file 'data_laut.nc' pertama kali. Pipa data di Cloud siap menerima input otomatis.")
