import streamlit as st
import math

# Podešavanje stranice
st.set_page_config(page_title="Deki LED Screen Kalkulejsn", page_icon="🖥️", layout="wide")

st.title("🖥️ Deki LED Screen Kalkulejsn")

# --- BAZA PANELA ---
baza_panela = {
    "P2.9 Plavi 168x168px": {"res_x": 168, "res_y": 168, "sirina": 500, "visina": 500, "tezina": 10, "potrosnja": 96.5},
    "P2.9 Crni 168x336px": {"res_x": 168, "res_y": 336, "sirina": 500, "visina": 1000, "tezina": 14, "potrosnja": 193},
    "P2.9S Crveni 176x168px": {"res_x": 176, "res_y": 168, "sirina": 500, "visina": 500, "tezina": 10, "potrosnja": 120},
    "P2.9C Zuti 168x168px": {"res_x": 168, "res_y": 168, "sirina": 500, "visina": 500, "tezina": 10, "potrosnja": 96.5},
    "P2.6 Plavi 192x192px": {"res_x": 192, "res_y": 192, "sirina": 500, "visina": 500, "tezina": 10, "potrosnja": 120},
    "P2.6C Zuti 192x192px": {"res_x": 192, "res_y": 192, "sirina": 500, "visina": 500, "tezina": 10, "potrosnja": 120}
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
    
    st.info("ℹ️ Režim rada: Indoor. Statika se računa prema odabranom tipu montaže.")

# --- PRORAČUNI ---
p_dopuna = baza_panela["P2.9 Plavi 168x168px"]

br_sirina = math.ceil((sirina_m * 1000) / p['sirina'])
br_visina_glavni = math.ceil((visina_m * 1000) / p['visina'])

broj_glavnih = br_sirina * br_visina_glavni
broj_dopunskih = br_sirina if half_meter else 0
ukupno_panela = broj_glavnih + broj_dopunskih

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
    opcije = [("125A", 82.5), ("63A", 40.5), ("32A", 22.5), ("16A", 10.5), ("Shuko Mono", 3)]
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
m1.metric("Panela", f"{ukupno_panela} kom", f"Glavni: {broj_glavnih} | Dopuna: {broj_dopunskih}")
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
    st.info(f"Glavnih: **{glavnih_data}**\n\nLinkova: **{ukupno_panela - glavnih_data}**")

with c2:
    st.subheader("Struja (Powercon)")
    st.write("Limit: **3000 W** po kablu")
    st.warning(f"Glavnih: **{glavnih_stru_izv}**\n\nLinkova: **{ukupno_panela - glavnih_stru_izv}**")

with c3:
    if tip_montaze == "Ground Support":
        st.subheader("Težina & Tegovi")
        st.write(f" Lokacija: **Indoor**")
        st.error(f"Kontra-teg: **{teg:.1f} kg**\n\nMasa ekrana: **{masa_ekrana:.1f} kg**")
    else:
        st.subheader("Težina & Rigging")
        st.write(f" Lokacija: **Hanging**")
        st.error(f"Ukupna masa: **{masa_ekrana:.1f} kg**")

st.divider()

# --- USLOVNI PRIKAZ SPECIFIKACIJE ---
if tip_montaze == "Ground Support":
    st.subheader("Specifikacija Ground Support elemenata")
    v = stvarna_v
    if v <= 1.0: balast_po_m = 0.0
    elif v <= 2.0: balast_po_m = 30.0
    elif v <= 3.0: balast_po_m = 70.0
    elif v <= 4.0: balast_po_m = 125.0
    else: balast_po_m = 125.0 + ((v - 4.0) * 50.0)

    grid_1m = int(stvarna_s // 1)
    ostatak_sirine = stvarna_s % 1
    grid_05m = 1 if ostatak_sirine > 0 else 0
    broj_stubova = grid_1m + grid_05m

    nivoi_u_vis = math.floor(v) if v >= 1.0 else 1 
    ukupno_backframe = broj_stubova * nivoi_u_vis
    teleskop_kom = (broj_stubova - 1) * nivoi_u_vis
    rear_brace_kom = ukupno_backframe
    ukupni_balast = stvarna_s * balast_po_m
    
    # Proračun gazišta: Dužina (stvarna_s) minus 1, samo ako je visina (v) > 2m
    gazista_kom = int(stvarna_s - 1) if v > 2.0 else 0

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.write(f"**Baza i stubovi**")
        st.write(f"- Grid (1m): **{grid_1m}** kom")
        if grid_05m > 0: st.write(f"- Grid (0.5m): **1** kom")
        st.write(f"- Ground Support: **{broj_stubova}** kom")
        st.write(f"- Backframe (1m): **{ukupno_backframe}** kom")
    with col_s2:
        st.write(f"**Povezivanje**")
        st.write(f"- Teleskop: **{teleskop_kom}** kom")
        st.write(f"- Snajper: **{rear_brace_kom}** kom")
        if gazista_kom > 0:
            st.write(f"- Gazišta: **{gazista_kom}** kom")
    with col_s3:
        st.write(f"**Balast (Tegovi)**")
        st.error(f"**Ukupno: {ukupni_balast:.1f} kg**")
        st.info(f"Po stopi: **{ukupni_balast/broj_stubova:.1f} kg**")

else:
    st.subheader("Specifikacija Hanging elemenata")
    grid_1m = int(stvarna_s // 1)
    grid_05m = 1 if (stvarna_s % 1) > 0 else 0
    shackles = (grid_1m + grid_05m) * 2
    plocice = math.ceil(kvadratura)
    srafovi = plocice * 4

    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        st.write(f"**Grid elementi**")
        st.write(f"- Grid (1m): **{grid_1m}** kom")
        if grid_05m > 0: st.write(f"- Grid (0.5m): **1** kom")
    with col_h2:
        st.write(f"**Rigging oprema**")
        st.write(f"- Gurtna: **{shackles}** kom")
        st.write(f"- Škopac: **{shackles}** kom")
        st.write(f"- Stezna kopča: **{shackles}** kom")
        st.write(f"- Okac: **{shackles}** kom")
    with col_h3:
        st.write(f"**Dodatni materijal**")
        st.write(f"- Pločice: **{plocice}** kom")
        st.write(f"- Šrafovi: **{srafovi}** kom")
        # Dodatna napomena ako je ekran viši od konstrukcije
if v > nivoi_u_vis:
    st.warning(f"⚠️ Ekran je viši od konstrukcije za {v - nivoi_u_vis}m. Gornji deo panela nema Backframe potporu.")
st.divider()
st.caption("v36 - by Dejan Popovic")



