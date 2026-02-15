import streamlit as st
import math

# Podešavanje stranice
st.set_page_config(page_title="Deki LED Screen Kalkulejsn", page_icon="🖥️", layout="wide")

st.title("🖥️ Deki LED Screen Kalkulejsn")

# --- BAZA PANELA ---
baza_panela = {
    "P2.9 Plavi 168x168px": {"res_x": 168, "res_y": 168, "sirina": 500, "visina": 500, "tezina": 8, "potrosnja": 96.5},
    "P2.9 Crni 168x336px": {"res_x": 168, "res_y": 336, "sirina": 500, "visina": 1000, "tezina": 12, "potrosnja": 193},
    "P2.9S Crveni 176x168px": {"res_x": 176, "res_y": 168, "sirina": 500, "visina": 500, "tezina": 8, "potrosnja": 120},
    "P2.9C Zuti 168x168px": {"res_x": 168, "res_y": 168, "sirina": 500, "visina": 500, "tezina": 8, "potrosnja": 96.5},
    "P2.6 Plavi 192x192px": {"res_x": 192, "res_y": 192, "sirina": 500, "visina": 500, "tezina": 8, "potrosnja": 120},
    "P2.6C Zuti 192x192px": {"res_x": 192, "res_y": 192, "sirina": 500, "visina": 500, "tezina": 8, "potrosnja": 120}
}

# --- SIDEBAR KONFIGURACIJA ---
with st.sidebar:
    st.header("⚙️ Postavke Ekrana")
    izbor = st.selectbox("Panel:", list(baza_panela.keys()))
    p = baza_panela[izbor]
    
    st.divider()
    sirina_m = st.number_input("Širina ekrana (m):", value=4.0, step=0.5)
    visina_m = st.number_input("Visina ekrana (m):", value=3.0, step=0.5)
    hercaza = st.selectbox("Frekvencija (Hz):", [50, 60, 100, 120, 144], index=1)
    
    st.divider()
    # OPCIJA ZA DODATNIH 0.5m (Half meter above)
    half_meter = st.checkbox("Dodaj 0.5m panel na vrh")
    
    st.info("ℹ️ Režim rada: Indoor. Statika se računa kao 70% mase ekrana radi stabilnosti konstrukcije.")

# --- PRORAČUNI ---
# Podaci za panel koji služi kao dopuna (0.5m)
p_dopuna = baza_panela["P2.9 Plavi 168x168px"]

# Broj panela po širini i visini
br_sirina = math.ceil((sirina_m * 1000) / p['sirina'])
br_visina_glavni = math.ceil((visina_m * 1000) / p['visina'])

# Ukupan broj panela
broj_glavnih = br_sirina * br_visina_glavni
broj_dopunskih = br_sirina if half_meter else 0
ukupno_panela = broj_glavnih + broj_dopunskih

# Stvarne dimenzije
stvarna_s = (br_sirina * p['sirina']) / 1000
stvarna_v = (br_visina_glavni * p['visina'] / 1000) + (0.5 if half_meter else 0.0)

# Rezolucija (sabiramo rezoluciju glavnih i dopunskog reda ako postoji)
res_x = p['res_x'] * br_sirina
res_y = (p['res_y'] * br_visina_glavni) + (p_dopuna['res_y'] if half_meter else 0)
ukupno_piksela = res_x * res_y

# Masa i Potrošnja
masa_ekrana = (broj_glavnih * p['tezina']) + (broj_dopunskih * p_dopuna['tezina'])
potrosnja_w = (broj_glavnih * p['potrosnja']) + (broj_dopunskih * p_dopuna['potrosnja'])

# ASPECT RATIO
gcd_val = math.gcd(res_x, res_y)
aspect_ratio = f"{res_x // gcd_val}:{res_y // gcd_val}"

# KABLOVI I LIMITI
pixel_limit = int((620928 * 60) / hercaza)
glavnih_data = math.ceil(ukupno_piksela / pixel_limit)
glavnih_struja = math.ceil(potrosnja_w / 3000)

# STATIKA (Indoor sigurnosni teg)
teg = masa_ekrana * 0.70

# --- PRIKAZ NA EKRANU ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Panela", f"{ukupno_panela} kom", f"Glavni: {broj_glavnih} | Dopuna: {broj_dopunskih}")
m2.metric("Dimenzije", f"{stvarna_s}m x {stvarna_v}m")
m3.metric("Rezolucija", f"{res_x}x{res_y} px", aspect_ratio)
m4.metric("Potrošnja", f"{potrosnja_w/1000:.2f} kW")

st.divider()

c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("📶 Data (Ethercon)")
    st.write(f"Limit (@{hercaza}Hz): **{pixel_limit:,} px**")
    st.info(f"Glavnih: **{glavnih_data}**\n\nLinkova: **{ukupno_panela - glavnih_data}**")

with c2:
    st.subheader("⚡ Struja (Powercon)")
    st.write("Limit: **3000 W** po kablu")
    st.warning(f"Glavnih: **{glavnih_struja}**\n\nLinkova: **{ukupno_panela - glavnih_struja}**")

with c3:
    st.subheader("⚓ Težina & Tegovi")
    st.write(f" Lokacija: **Indoor**")
    st.error(f"Kontra-teg: **{teg:.1f} kg**\n\nMasa ekrana: **{masa_ekrana:.1f} kg**")

st.divider()
st.caption("v26 - Deki LED Screen Kalkulejsn")
