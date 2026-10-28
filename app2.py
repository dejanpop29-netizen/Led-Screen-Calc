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
m1.metric("Panela", f"{ukupno_panela} kom", f"Glavni: {broj_glavnih} | Dopuna: {broj_dopunskih} | Kejseva: {ukupno_kejseva}")
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
    st.info(f"Preporučeno linija: **{glavnih_data}**")

with c2:
    st.subheader("Struja (Powercon)")
    st.write("Limit: **3000 W** po kablu")
    st.warning(f"Preporučeno izvoda: **{glavnih_stru_izv}**")

with c3:
    if tip_montaze == "Ground Support":
        st.subheader("Težina & Tegovi")
        st.write("Lokacija: **Indoor**")
        st.error(f"Težina ekrana: **{masa_ekrana:.1f} kg**\n\nKontra-teg: **{teg:.1f} kg**")
    else:
        st.subheader("Težina & Rigging")
        st.write("Lokacija: **Hanging**")
        st.error(f"Težina ekrana: **{masa_ekrana:.1f} kg**")

st.divider()

# --- PALETA BOJA ZA LINIJE ---
boje_linija = [
    "#0083b8", # Plava
    "#28a745", # Zelena
    "#ffc107", # Žuta
    "#e83e8c", # Roza
    "#6f42c1", # Ljubičasta
    "#fd7e14", # Narandžasta
    "#20c997", # Tirkizna
    "#6c757d"  # Siva
]

def get_boja(index_linije):
    return boje_linija[(index_linije - 1) % len(boje_linija)]

# --- PAMETNA RAVNOMERNA PODELA LINIJA ---
# Automatski delimo ukupan broj panela na tačno onoliko jednakih delova 
# koliko nalažu minimalni tehnički limiti (glavnih_stru_izv / glavnih_data),
# tako da svaka linija ima identičan broj panela (npr. 60 panela / 3 linije = tačno 20 po liniji).

broj_strujnih_linija = max(1, glavnih_stru_izv)
panela_po_strujnoj_liniji = math.ceil(ukupno_panela / broj_strujnih_linija)

broj_data_linija = max(1, glavnih_data)
panela_po_data_liniji = math.ceil(ukupno_panela / broj_data_linija)

base_w = 60
main_h = int(base_w * (p['visina'] / p['sirina']))
dop_h = int(base_w * (p_dopuna['visina'] / p_dopuna['sirina'])) if half_meter else 30

# ==========================================
# 1. STRUJNE LINIJE (RAVNOMERNO RASPOREĐENE)
# ==========================================
st.subheader("⚡ Vizuelni prikaz strujnih linija (Powercon - Ravnomerne grupe)")
st.markdown(f"Ukupno **{broj_strujnih_linija}** strujna/e izvoda, sa ravnomerno raspoređenim panelima po liniji.")

struja_html = ""
p_idx = 0

if half_meter:
    struja_html += '<div style="display: flex; gap: 4px; justify-content: center; margin-bottom: 4px;">'
    for _ in range(br_sirina):
        p_idx += 1
        s_line = min(broj_strujnih_linija, math.ceil(p_idx / panela_po_strujnoj_liniji))
        boja = get_boja(s_line)
        struja_html += f'''
        <div style="width: {base_w}px; height: {dop_h}px; background-color: {boja}; border: 1px solid #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 8px; color: white; font-weight: bold; border-radius: 3px;" title="0.5m Panel | Struja S{s_line}">
            <span>0.5m</span>
            <span style="font-size: 7px; background: rgba(0,0,0,0.3); padding: 1px 3px; border-radius: 2px;">S{s_line}</span>
        </div>'''
    struja_html += '</div>'

for row in range(br_visina_glavni):
    struja_html += '<div style="display: flex; gap: 4px; justify-content: center; margin-bottom: 4px;">'
    for col in range(br_sirina):
        p_idx += 1
        s_line = min(broj_strujnih_linija, math.ceil(p_idx / panela_po_strujnoj_liniji))
        boja = get_boja(s_line)
        struja_html += f'''
        <div style="width: {base_w}px; height: {main_h}px; background-color: {boja}; border: 1px solid #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 9px; color: white; font-weight: bold; border-radius: 3px;" title="Panel P{p_idx} | Struja S{s_line}">
            <span>P{p_idx}</span>
            <span style="font-size: 7px; background: rgba(0,0,0,0.3); padding: 1px 3px; border-radius: 2px;">S{s_line}</span>
        </div>'''
    struja_html += '</div>'

grid_struja = f"""
<div style="background-color: #0e1117; padding: 15px; border-radius: 8px; border: 1px solid #303545; overflow-x: auto; text-align: center;">
    {struja_html}
    <p style="font-size: 11px; color: #a0a0a0; margin-top: 10px; font-family: sans-serif;">
        ⚡ Broj strujnih linija: <b>{broj_strujnih_linija}</b> (~{panela_po_strujnoj_liniji} panela po liniji)
    </p>
</div>
"""
st.components.v1.html(grid_struja, height=110 + ((br_visina_glavni * main_h) + (dop_h if half_meter else 0)))

st.divider()

# ==========================================
# 2. DATA / SIGNALNE LINIJE (RAVNOMERNO RASPOREĐENE)
# ==========================================
st.subheader("🌐 Vizuelni prikaz data / signalnih linija (Ethercon - Ravnomerne grupe)")
st.markdown(f"Ukupno **{broj_data_linija}** data linija (@{hercaza}Hz), ravnomerno podeljenih.")

data_html = ""
p_idx = 0

if half_meter:
    data_html += '<div style="display: flex; gap: 4px; justify-content: center; margin-bottom: 4px;">'
    for _ in range(br_sirina):
        p_idx += 1
        d_line = min(broj_data_linija, math.ceil(p_idx / panela_po_data_liniji))
        boja = get_boja(d_line)
        data_html += f'''
        <div style="width: {base_w}px; height: {dop_h}px; background-color: {boja}; border: 1px solid #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 8px; color: white; font-weight: bold; border-radius: 3px;" title="0.5m Panel | Data D{d_line}">
            <span>0.5m</span>
            <span style="font-size: 7px; background: rgba(0,0,0,0.3); padding: 1px 3px; border-radius: 2px;">D{d_line}</span>
        </div>'''
    data_html += '</div>'

for row in range(br_visina_glavni):
    data_html += '<div style="display: flex; gap: 4px; justify-content: center; margin-bottom: 4px;">'
    for col in range(br_sirina):
        p_idx += 1
        d_line = min(broj_data_linija, math.ceil(p_idx / panela_po_data_liniji))
        boja = get_boja(d_line)
        data_html += f'''
        <div style="width: {base_w}px; height: {main_h}px; background-color: {boja}; border: 1px solid #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 9px; color: white; font-weight: bold; border-radius: 3px;" title="Panel P{p_idx} | Data D{d_line}">
            <span>P{p_idx}</span>
            <span style="font-size: 7px; background: rgba(0,0,0,0.3); padding: 1px 3px; border-radius: 2px;">D{d_line}</span>
        </div>'''
    data_html += '</div>'

grid_data = f"""
<div style="background-color: #0e1117; padding: 15px; border-radius: 8px; border: 1px solid #303545; overflow-x: auto; text-align: center;">
    {data_html}
    <p style="font-size: 11px; color: #a0a0a0; margin-top: 10px; font-family: sans-serif;">
        🌐 Broj data linija: <b>{broj_data_linija}</b> (~{panela_po_data_liniji} panela po liniji)
    </p>
</div>
"""
st.components.v1.html(grid_data, height=110 + ((br_visina_glavni * main_h) + (dop_h if half_meter else 0)))

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
    
    gazista_kom = int(math.ceil(stvarna_s) - 1) if v > 2.0 else 0
    gazista_tegova_kom = math.ceil(stvarna_s / 2) if v > 2.0 else 0

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.write("**Baza i stubovi**")
        st.write(f"- Grid (1m): **{grid_1m}** kom")
        if grid_05m > 0: st.write(f"- Grid (0.5m): **1** kom")
        st.write(f"- Ground Support: **{broj_stubova}** kom")
        st.write(f"- Backframe (1m): **{ukupno_backframe}** kom")
    with col_s2:
        st.write("**Povezivanje**")
        st.write(f"- Teleskop: **{teleskop_kom}** kom")
        st.write(f"- Snajper: **{rear_brace_kom}** kom")
        if gazista_kom > 0:
            st.write(f"- Gazišta (ekran): **{gazista_kom}** kom")
        if gazista_tegova_kom > 0:
            st.write(f"- Gazišta (tegovi): **{gazista_tegova_kom}** kom")
    with col_s3:
        st.write("**Balast (Tegovi)**")
        st.error(f"**Ukupno: {ukupni_balast:.1f} kg**")
        st.info(f"Po stopi: **{ukupni_balast/broj_stubova:.1f} kg**")

    if v > nivoi_u_vis:
        st.warning(f"⚠️ Ekran je viši od konstrukcije za {round(v - nivoi_u_vis, 2)}m. Gornji deo panela nema Backframe potporu.")

else:
    st.subheader("Specifikacija Hanging elemenata")
    grid_1m = int(stvarna_s // 1)
    grid_05m = 1 if (stvarna_s % 1) > 0 else 0
    shackles = (grid_1m + grid_05m) * 2
    plocice = math.ceil(kvadratura)
    srafovi = plocice * 4

    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        st.write("**Grid elementi**")
        st.write(f"- Grid (1m): **{grid_1m}** kom")
        if grid_05m > 0: st.write(f"- Grid (0.5m): **1** kom")
    with col_h2:
        st.write("**Rigging oprema**")
        st.write(f"- Gurtna: **{shackles}** kom")
        st.write(f"- Škopac: **{shackles}** kom")
        st.write(f"- Stezna kopča: **{shackles}** kom")
        st.write(f"- Okac: **{shackles}** kom")
    with col_h3:
        st.write("**Dodatni materijal**")
        st.write(f"- Pločice: **{plocice}** kom")
        st.write(f"- Šrafovi: **{srafovi}** kom")

st.divider()
st.caption("v47 - by Dejan Popovic")

# Učitavanje logo fajla
try:
    st.image("logo.png", width=180)
except:
    st.write("PROSOUND")
