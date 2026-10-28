import streamlit as st
import math

# Podešavanje stranice
st.set_page_config(page_title="Deki LED Screen Kalkulejsn", page_icon="🖥️", layout="wide")

st.title("🖥️ Deki LED Screen Kalkulejsn")

# --- BAZA PANELA (sa brojem panela po kejsu) ---
baza_panela = {
    "P3.9 Crni 128x128px": {"res_x": 128, "res_y": 128, "sirina": 500, "visina": 500, "tezina": 10, "potrosnja": 170, "po_kejsu": 10},
    "P3.9 Crni 128x256px": {"res_x": 128, "res_y": 256, "sirina": 500, "visina": 1000, "tezina": 15, "potrosnja": 330, "po_kejsu": 5},
    "P2.9 Plavi 168x168px": {"res_x": 168, "res_y": 168, "sirina": 500, "visina": 500, "tezina": 10, "potrosnja": 120, "po_kejsu": 10},
    "P2.9 Crni 168x336px": {"res_x": 168, "res_y": 336, "sirina": 500, "visina": 1000, "tezina": 15, "potrosnja": 240, "po_kejsu": 5},
    "P2.9S Crveni 176x168px": {"res_x": 176, "res_y": 168, "sirina": 500, "visina": 500, "tezina": 10, "potrosnja": 120, "po_kejsu": 10},
    "P2.9C Zuti 168x168px": {"res_x": 168, "res_y": 168, "sirina": 500, "visina": 500, "tezina": 10, "potrosnja": 120, "po_kejsu": 10},
    "P2.6 Plavi 192x192px": {"res_x": 192, "res_y": 192, "sirina": 500, "visina": 500, "tezina": 10, "potrosnja": 120, "po_kejsu": 10},
    "P2.6C Zuti 192x192px": {"res_x": 192, "res_y": 192, "sirina": 500, "visina": 500, "tezina": 10, "potrosnja": 120, "po_kejsu": 10}
}

# --- SIDEBAR KONFIGURACIJA ---
with st.sidebar:
    st.header("⚙️ Postavke Ekrana")
    izbor = st.selectbox("Panel:", list(baza_panela.keys()))
    p = baza_panela[izbor]
     
    st.divider()
    sirina_m = st.number_input("Širina ekrana (m):", value=4.0, step=0.5)
    visina_m = st.number_input("Visina ekrana (m):", value=3.0, step=0.5)
    half_meter = st.checkbox("Dodaj 0.5m panel na vrh")
    hercaza = st.selectbox("Frekvencija (Hz):", [50, 60, 100, 120, 144], index=1)
     
    st.divider()
    tip_montaze = st.radio("Tip montaže:", ["Ground Support", "Hanging"])
    
    st.info("ℹ️ Režim rada: Indoor. Kontra-teg se računa kao 70% mase ekrana radi stabilnosti konstrukcije.")

# --- PRORAČUNI ---
if "P3.9" in izbor:
    p_dopuna = baza_panela["P3.9 Crni 128x128px"]
else:
    p_dopuna = baza_panela["P2.9 Plavi 168x168px"]
    
br_sirina = math.ceil((sirina_m * 1000) / p['sirina'])
br_visina_glavni = math.ceil((visina_m * 1000) / p['visina'])

broj_glavnih = br_sirina * br_visina_glavni
broj_dopunskih = br_sirina if half_meter else 0
ukupno_panela = broj_glavnih + broj_dopunskih

kejs_glavnih = math.ceil(broj_glavnih / p['po_kejsu'])
kejs_dopunskih = math.ceil(broj_dopunskih / p_dopuna['po_kejsu']) if broj_dopunskih > 0 else 0
ukupno_kejseva = kejs_glavnih + kejs_dopunskih

stvarna_s = (br_sirina * p['sirina']) / 1000
stvarna_v = (br_visina_glavni * p['visina'] / 1000) + (0.5 if half_meter else 0.0)
kvadratura = stvarna_s * stvarna_v

res_x = p['res_x'] * br_sirina
res_y = (p['res_y'] * br_visina_glavni) + (p_dopuna['res_y'] if half_meter else 0)
ukupno_piksela = res_x * res_y

masa_ekrana = (broj_glavnih * p['tezina']) + (broj_dopunskih * p_dopuna['tezina'])
potrosnja_w = (broj_glavnih * p['potrosnja']) + (broj_dopunskih * p_dopuna['potrosnja'])
potrosnja_kw = potrosnja_w / 1000

# --- KOMBINATORIKA STRUJNOG PRIKLJUČKA ---
def izracunaj_prikljucke(snaga):
    if snaga <= 0: return "Bez potrošnje"
    opcije = [("125A", 82), ("63A", 40), ("32A", 22), ("16A", 10), ("Shuko Mono", 3)]
    rezultat = []
    ostatak = snaga
    for naziv, kapacitet in opcije:
        broj = int(ostatak // kapacitet)
        if broj > 0:
            rezultat.append(f"{broj} x {naziv}")
            ostatak %= kapacitet
    if ostatak > 0:
        rezultat.append("1 x Shuko Mono")
    return " + ".join(rezultat)

prikljucak = izracunaj_prikljucke(potrosnja_kw)

# ASPECT RATIO
gcd_val = math.gcd(res_x, res_y)
aspect_ratio = f"{res_x // gcd_val}:{res_y // gcd_val} ({ukupno_piksela:,} px)"

# KABLOVI I LIMITI
pixel_limit = int((620928 * 60) / hercaza)
glavnih_data = math.ceil(ukupno_piksela / pixel_limit)
glavnih_stru_izv = math.ceil(potrosnja_w / 3000)

# STATIKA
teg = masa_ekrana * 0.70

# --- PRIKAZ NA EKRANU ---
m1, m2, m3 = st.columns(3)
m1.metric("Panela", f"{ukupno_panela} kom", f"Glavni: {br_sirina * br_visina_glavni} | Dopuna: {broj_dopunskih} | Kejseva: {ukupno_kejseva}")
m2.metric("Dimenzije", f"{stvarna_s}m x {stvarna_v}m", f"{kvadratura:.2f} m²")
m3.metric("Rezolucija", f"{res_x}x{res_y} px", aspect_ratio)

st.divider()
st.subheader(f"Potrošnja: {potrosnja_kw:.2f} kW")
st.write(f"Strujni priključak: {prikljucak}")
st.divider()

c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("Data (Ethercon)")
    st.write(f"Limit (@{hercaza}Hz): **{pixel_limit:,} px**")
    st.info(f"Glavnih data linija: **{glavnih_data}**\n\nLinkovanih panela: **{ukupno_panela - glavnih_data}**")

with c2:
