# AeroOceanic_AI

A small, in-progress prototype dashboard for surface currents along the Cisadane coast (Jakarta Bay, Indonesia).

## What it does

- `engine.py` builds a 24-hour, 40 × 40 surface-current field (106.60–107.10°E, 6.20–5.80°S):
  - tidal current from an analytical M2 + K1 harmonic signal (fixed amplitudes and phases),
  - plus a simple wind term from hourly 10 m wind fetched from the [Open-Meteo](https://open-meteo.com/) API (falls back to a constant 5 m/s north-westerly wind if the request fails),
  - and writes the result to `data_laut.nc` (u, v and speed) with xarray.
- `app.py` is a Streamlit dashboard that runs `engine.py` if needed and plots current speed and vectors for a selected hour.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Limitations

- This is not a hydrodynamic model: the spatial pattern is a prescribed linear scaling, not a solution of the shallow-water equations.
- Tidal constants are illustrative, not fitted to observations.
- The simulation date is currently hard-coded (20 May 2026).
- There is no machine-learning component yet, and the output has not been validated against observations.

## Next steps

- Validate against real current observations (e.g., ADCP or tide-gauge data).
- Replace the prescribed field with output from a proper hydrodynamic model.

## Author

Moh. Adli Daffa Amrullah
