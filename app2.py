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
    smer_povezivanja = st.radio("Smer linija kablova:", ["Zmijoliko (Snake po redovima)", "Vertikalno (Po kolonama)"])
    
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
    st.info(f"Preporučeno portova: **{glavnih_data}**")

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
        st.info(f"Po stopi(Ground Support): **{ukupni_balast/broj_stubova:.1f} kg**")

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

# --- PALETA BOJA ZA PORTOVE ---
boje_portova = [
    "#e53935", # Crvena (Port 1)
    "#43a047", # Zelena (Port 2)
    "#00acc1", # Tirkizna (Port 3)
    "#8e24aa", # Ljubičasta (Port 4)
    "#fb8c00", # Narandžasta (Port 5)
    "#1e88e5", # Plava (Port 6)
    "#d81b60", # Roza (Port 7)
    "#6d4c41"  # Smeđa (Port 8)
]

def get_boja_porta(p_idx):
    return boje_portova[(p_idx - 1) % len(boje_portova)]

# --- MATRICA PANELA I MAPIRANJE PORTOVA ---
matrica_panela = []

if half_meter:
    red_dopuna = []
    for col in range(br_sirina):
        red_dopuna.append({"tip": "dopuna", "r": -1, "c": col})
    matrica_panela.append(red_dopuna)

for row in range(br_visina_glavni):
    red_glavni = []
    for col in range(br_sirina):
        red_glavni.append({"tip": "glavni", "r": row, "c": col})
    matrica_panela.append(red_glavni)

uk_redova = len(matrica_panela)
panel_indeksi_mapa = {} 

p_brojac = 0
if "Vertikalno" in smer_povezivanja:
    for col in range(br_sirina):
        for row in range(uk_redova - 1, -1, -1):
            p_brojac += 1
            panel_indeksi_mapa[(row, col)] = p_brojac
else:
    for row in range(uk_redova):
        cols_iter = range(br_sirina) if row % 2 == 0 else range(br_sirina - 1, -1, -1)
        for col_idx in cols_iter:
            p_brojac += 1
            panel_indeksi_mapa[(row, col_idx)] = p_brojac

# Raspodela panela po portovima na osnovu pixel limita
port_mapa_p = {}
port_stat = {} # {port_id: {"cab": count, "px": pixels}}

trenutni_port = 1
trenutni_px_porta = 0
panel_pix_jedn = (p['res_x'] * p['res_y'])

for r_idx, red in enumerate(matrica_panela):
    for c_idx, panel in enumerate(red):
        p_idx = panel_indeksi_mapa[(r_idx, c_idx)]
        p_pix = (p_dopuna['res_x'] * p_dopuna['res_y']) if panel["tip"] == "dopuna" else panel_pix_jedn
        
        if trenutni_px_porta + p_pix > pixel_limit and trenutni_port < glavnih_data:
            trenutni_port += 1
            trenutni_px_porta = 0
            
        port_mapa_p[(r_idx, c_idx)] = trenutni_port
        trenutni_px_porta += p_pix
        
        if trenutni_port not in port_stat:
            port_stat[trenutni_port] = {"cab": 0, "px": 0}
        port_stat[trenutni_port]["cab"] += 1
        port_stat[trenutni_port]["px"] += p_pix

# Pronalazimo početni panel (IN) za svaki port da dobije kružnu oznaka porta (1, 2, 3...)
port_min_panel = {}
for r_idx, red in enumerate(matrica_panela):
    for c_idx, panel in enumerate(red):
        p_id = panel_indeksi_mapa[(r_idx, c_idx)]
        port_id = port_mapa_p[(r_idx, c_idx)]
        if port_id not in port_min_panel or p_id < port_min_panel[port_id]:
            port_min_panel[port_id] = p_id

# --- VIZUELNI PRIKAZ PORTOVA U STILU KARTICE SA SLIKE ---
def generisi_vizuelne_portove():
    veliki_ekran = stvarna_s > 15.0
    odnos_glavni = p['visina'] / p['sirina']
    odnos_dopuna = (p_dopuna['visina'] / p_dopuna['sirina']) if half_meter else 0.5
    
    if veliki_ekran:
        sirina_css = "60px"
        visina_glavni_px = int(60 * odnos_glavni)
        visina_dopuna_px = int(60 * odnos_dopuna)
        min_sirina_px = br_sirina * 64
        skrol_stil = "overflow-x: auto;"
    else:
        sirina_css = f"calc({100 / br_sirina}% - 2px)"
        bazna_sirina_px = max(25, min(90, int(800 / br_sirina)))
        visina_glavni_px = int(bazna_sirina_px * odnos_glavni)
        visina_dopuna_px = int(bazna_sirina_px * odnos_dopuna)
        min_sirina_px = 0
        skrol_stil = "overflow-x: hidden;"

    # Generisanje legende portova gore
    legend_html = '<div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 15px; background: #161b22; padding: 12px; border-radius: 6px; border: 1px solid #303545;">'
    for pid, data in port_stat.items():
        boja = boje_portova[(pid - 1) % len(boje_portova)]
        procenat = int((data["px"] / pixel_limit) * 100)
        legend_html += f'''
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 14px; height: 14px; background-color: {boja}; border-radius: 3px;"></div>
            <span style="font-size: 12px; color: #ffffff; font-family: sans-serif;"><b>Port {pid}</b> ({data["cab"]} cab., {data["px"]:,}px, {procenat}%)</span>
        </div>'''
    legend_html += '</div>'

    html_out = f"""
    <div style="background-color: #0e1117; padding: 15px; border-radius: 8px; border: 1px solid #303545; width: 100%; box-sizing: border-box;">
        {legend_html}
        <div style="{skrol_stil} width: 100%;">
            <div style="min-width: {min_sirina_px}px; border: 2px solid #ffffff; padding: 4px; background: #0b0e14;">
    """
    
    for row_idx, red in enumerate(matrica_panela):
        html_out += '<div style="display: flex; gap: 2px; justify-content: center; margin-bottom: 2px; width: 100%;">'
        for col_idx, panel in enumerate(red):
            p_idx = panel_indeksi_mapa[(row_idx, col_idx)]
            port_id = port_mapa_p[(row_idx, col_idx)]
            boja = get_boja_porta(port_id)
            
            h_visina = f"{visina_dopuna_px}px" if panel["tip"] == "dopuna" else f"{visina_glavni_px}px"
            tekst_vrsta = "0.5m" if panel["tip"] == "dopuna" else f"P{p_idx}"
            
            # Kružna oznaka početka porta sa brojem u stilu sa slike (npr. krug sa brojem 1, 2...)
            kruzni_pocetak = ""
            if p_idx == port_min_panel.get(port_id):
                kruzni_pocetak = f'''
                <div style="width: 18px; height: 18px; border: 2px solid #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 9px; background: rgba(0,0,0,0.6); color: #fff; margin-bottom: 1px; font-weight: bold;">
                    {port_id}
                </div>'''
            
            # Strelica smera
            strelica = "➔"
            if "Vertikalno" in smer_povezivanja:
                strelica = "⬆"
            else:
                if row_idx % 2 != 0:
                    strelica = "⬅"
                else:
                    strelica = "➔"

            html_out += f'''
            <div style="width: {sirina_css}; min-width: {sirina_css if veliki_ekran else '0'}; height: {h_visina}; background-color: {boja}; border: 1px solid rgba(255,255,255,0.4); display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 9px; color: white; font-weight: bold; border-radius: 2px;" title="Panel {p_idx} | Port {port_id}">
                {kruzni_pocetak}
                <span style="font-size: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{tekst_vrsta} {strelica}</span>
                <span style="font-size: 7px; background: rgba(0,0,0,0.4); padding: 1px 2px; border-radius: 2px; margin-top: 1px;">{port_id}.{p_idx}</span>
            </div>'''
        html_out += '</div>'
        
    html_out += f"""
            </div>
        </div>
        <p style="font-size: 11px; color: #a0a0a0; margin-top: 10px; text-align: center; font-family: sans-serif;">
            🌐 Ukupno aktivnih portova: <b>{len(port_stat)}</b> (@{hercaza}Hz) — <i>Prikaz sa oznakama portova i smerom kabliranja</i>
        </p>
    </div>
    """
    return html_out

# Dinamička visina okvira
odnos_v = p['visina'] / p['sirina']
visina_reda_px = int(55 * odnos_v) if stvarna_s > 15.0 else max(30, int(800 / br_sirina * odnos_v))
visina_ifrejma = 160 + (uk_redova * (visina_reda_px + 6))

st.subheader("🌐 Vizuelna mapa portova i signala (Sender Port Map)")
st.markdown(f"Režim povezivanja: **{smer_povezivanja}**")
grid_portova_html = generisi_vizuelne_portove()
st.components.v1.html(grid_portova_html, height=visina_ifrejma)

st.divider()
st.caption("v58 - by Dejan Popovic")

# Učitavanje logo fajla
try:
    st.image("logo.png", width=180)
except:
    st.write("PROSOUND")
