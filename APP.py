import streamlit as st
import sqlite3
import pandas as pd

# Configuració de la pàgina
st.set_page_config(page_title="Big Rocks - Sorigué", layout="wide", page_icon="🪨")

# CSS Corporatiu (Cian Sorigué aproximat #009FE3) i ajustos de disseny
st.markdown("""
    <style>
    .stButton>button[kind="primary"] {
        background-color: #009FE3 !important;
        color: white !important;
        border-color: #009FE3 !important;
    }
    /* Fem que els 'radio buttons' s'alineïn millor amb la resta d'elements */
    div[role="radiogroup"] {
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. CONFIGURACIÓ DE LA BASE DE DADES
# ==========================================
def init_db():
    conn = sqlite3.connect('bigrocks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuaris (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS big_rocks (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, mes TEXT, nom TEXT, persones TEXT, reunions TEXT, notes_progres TEXT, pregunta TEXT, passos TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tars (id INTEGER PRIMARY KEY AUTOINCREMENT, id_br INTEGER, num TEXT, descripcio TEXT, progres INTEGER, estat TEXT, FOREIGN KEY(id_br) REFERENCES big_rocks(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS mesos_tancats (username TEXT, mes TEXT, PRIMARY KEY(username, mes))''') 
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=()):
    conn = sqlite3.connect('bigrocks.db')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    return c

def fetch_query(query, params=()):
    conn = sqlite3.connect('bigrocks.db')
    c = conn.cursor()
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

# Funció per dibuixar la nova barra de progrés integrada
def progress_bar_colorida(progres, is_global=False):
    # Colors de l'escala
    if progres <= 25: 
        color = "#FF4B4B" # Vermell
    elif progres <= 50: 
        color = "#FFA500" # Taronja
    elif progres <= 99: 
        color = "#FFD700" # Groc
    else: 
        color = "#00C851" # Verd
        
    # Ajustos visuals depenent de si és la barra global o la d'un TAR
    height = "32px" if is_global else "36px"
    margin = "5px 0 15px 0" if is_global else "2px 0 0 0"
    text = f"Avenç global: {progres}%" if is_global else f"{progres}%"
    
    # Text fosc per fons clars (groc/taronja) i text blanc per fons foscos
    text_color = "#333" if progres == 0 or (is_global and 25 < progres <= 99) else "white"
    
    html = f"""
    <div style="width: 100%; background-color: #f0f2f6; border-radius: 6px; height: {height}; position: relative; margin: {margin}; border: 1px solid #e0e0e0;">
        <div style="width: {progres}%; background-color: {color}; height: 100%; border-radius: 5px; transition: width 0.3s ease-in-out;"></div>
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-family: sans-serif; font-size: 14px; font-weight: bold; color: {text_color}; text-shadow: {'1px 1px 2px rgba(0,0,0,0.2)' if text_color == 'white' else 'none'};">
            {text}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# Callbacks per actualitzar l'estat evitant retards en la UI
def actualitzar_progres_tar_cb(tar_id, key):
    nou_progres = st.session_state[key]
    run_query("UPDATE tars SET progres=? WHERE id=?", (nou_progres, tar_id))

def actualitzar_text_tar_cb(tar_id, key):
    nova_desc = st.session_state[key]
    run_query("UPDATE tars SET descripcio=? WHERE id=?", (nova_desc, tar_id))

def arxivar_tar(id_tar): 
    run_query("UPDATE tars SET estat='Arxivat' WHERE id=?", (id_tar,))
    
def actualitzar_notes_br(id_br, notes, pregunta, passos): 
    run_query("UPDATE big_rocks SET notes_progres=?, pregunta=?, passos=? WHERE id=?", (notes, pregunta, passos, id_br))

# ==========================================
# 2. SISTEMA DE LOGIN
# ==========================================
if 'usuari_actual' not in st.session_state: st.session_state.usuari_actual = None

if st.session_state.usuari_actual is None:
    try:
        st.image("sorigue_logo_RGB-positivo.png", width=300)
    except:
        st.title("🪨 Sistema Big Rocks")
        
    st.subheader("🔐 Accés a la Plataforma")
    tab1, tab2 = st.tabs(["Iniciar Sessió", "Registrar Nou Usuari"])
    
    with tab1:
        with st.form("login_form"):
            usuari = st.text_input("Nom d'usuari")
            contrasenya = st.text_input("Contrasenya", type="password")
            if st.form_submit_button("Entrar", type="primary"):
                if fetch_query("SELECT * FROM usuaris WHERE username=? AND password=?", (usuari, contrasenya)):
                    st.session_state.usuari_actual = usuari
                    st.session_state.mes_actual = "Juliol 2026"
                    st.session_state.pantalla = 'dashboard'
                    st.rerun()
                else:
                    st.error("Usuari o contrasenya incorrectes.")
    with tab2:
        with st.form("register_form"):
            nou_usuari = st.text_input("Nou nom d'usuari")
            nova_contra = st.text_input("Contrasenya", type="password")
            if st.form_submit_button("Registrar", type="primary"):
                try:
                    run_query("INSERT INTO usuaris (username, password) VALUES (?, ?)", (nou_usuari, nova_contra))
                    st.success("Usuari creat correctament! Ara pots iniciar sessió.")
                except sqlite3.IntegrityError:
                    st.error("Aquest nom d'usuari ja existeix.")
    st.stop()

# ==========================================
# 3. SIDEBAR (NAVEGACIÓ I HISTÒRIC)
# ==========================================
USUARI = st.session_state.usuari_actual

st.sidebar.write(f"👤 Connectat com: **{USUARI}**")

mesos_disponibles = [row[0] for row in fetch_query("SELECT DISTINCT mes FROM big_rocks WHERE username=?", (USUARI,))]
if "Juliol 2026" not in mesos_disponibles: mesos_disponibles.insert(0, "Juliol 2026") 

mes_seleccionat = st.sidebar.selectbox("📅 Navegar pels mesos:", mesos_disponibles, index=mesos_disponibles.index(st.session_state.mes_actual) if st.session_state.mes_actual in mesos_disponibles else 0)
st.session_state.mes_actual = mes_seleccionat

MES = st.session_state.mes_actual

mes_tancat_db = fetch_query("SELECT * FROM mesos_tancats WHERE username=? AND mes=?", (USUARI, MES))
es_tancat = len(mes_tancat_db) > 0

if es_tancat:
    st.sidebar.error("🔒 Aquest mes està TANCAT.")
    if st.sidebar.button("🔓 Desbloquejar Mes"):
        run_query("DELETE FROM mesos_tancats WHERE username=? AND mes=?", (USUARI, MES))
        st.rerun()
else:
    st.sidebar.success("✏️ Mes Obert (Editable)")

st.sidebar.markdown("---")
if st.sidebar.button("Tancar Sessió"):
    st.session_state.usuari_actual = None
    st.rerun()

# ==========================================
# 4. PANTALLA PRINCIPAL: DASHBOARD
# ==========================================
if 'pantalla' not in st.session_state: st.session_state.pantalla = 'dashboard'
if 'mostrar_formulari_br' not in st.session_state: st.session_state.mostrar_formulari_br = False

if st.session_state.pantalla == 'dashboard':
    
    # Logo a dalt de tot de la pantalla de Big Rocks
    try:
        st.image("sorigue_logo_RGB-positivo.png", width=250)
    except:
        pass
        
    col_titol, col_boto = st.columns([3, 1])
    with col_titol:
        st.title(f"🪨 Dashboard - {MES}")
    with col_boto:
        st.write("<br>", unsafe_allow_html=True)
        if not es_tancat:
            st.button("📊 Avaluar i Tancar Mes", type="primary", use_container_width=True, on_click=lambda: st.session_state.update(pantalla='resum'))
    st.markdown("---")

    brs = fetch_query("SELECT id, nom, persones, reunions, notes_progres, pregunta, passos FROM big_rocks WHERE username=? AND mes=?", (USUARI, MES))

    if not brs:
        st.info("No hi ha cap Big Rock. Afegeix-ne de noves a sota.")
    else:
        for br in brs:
            br_id = br[0]
            with st.container():
                st.markdown(f"## 🎯 {br[1]}")
                st.caption(f"👥 **Persones clau:** {br[2]} | 📅 **Reunions:** {br[3]}")
                
                tars = fetch_query("SELECT id, num, descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu'", (br_id,))
                progres_mitja = int(sum(t[3] for t in tars) / len(tars)) if tars else 0
                
                # Barra global de la Big Rock amb escala de colors i text integrat
                progress_bar_colorida(progres_mitja, is_global=True)
                
                for tar in tars:
                    tar_id, num, desc, progres = tar
                    # Forcem que el progress només sigui 0, 50 o 100 per si hi ha dades velles
                    if progres not in [0, 50, 100]: progres = 0
                    
                    # Estructura de columnes actualitzada: 
                    # Col1: TAR X | Col2: Descripció | Col3: Selector 0/50/100 | Col4: Barra Visual | Col5: Paperera
                    col1, col2, col3, col4, col5 = st.columns([1, 4, 3, 2, 1])
                    
                    with col1: 
                        st.write(f"**{num}**")
                    with col2:
                        k_desc = f"desc_{tar_id}"
                        st.text_input("Desc", value=desc, key=k_desc, label_visibility="collapsed", disabled=es_tancat,
                                      on_change=actualitzar_text_tar_cb, args=(tar_id, k_desc))
                    with col3:
                        k_radio = f"radio_{tar_id}"
                        st.radio("Estat", options=[0, 50, 100], format_func=lambda x: f"{x}%", 
                                 index=[0, 50, 100].index(progres), horizontal=True, key=k_radio, 
                                 label_visibility="collapsed", disabled=es_tancat,
                                 on_change=actualitzar_progres_tar_cb, args=(tar_id, k_radio))
                    with col4:
                        # La barra visual maca al costat mateix del selector
                        progress_bar_colorida(progres, is_global=False)
                    with col5:
                        st.button("🗑️", key=f"btn_{tar_id}", on_click=arxivar_tar, args=(tar_id,), disabled=es_tancat)
                
                with st.expander("📝 Detalls, Preguntes i Pròxims Passos", expanded=False):
                    notes = st.text_area("Progreso:", value=br[4], key=f"notes_{br_id}", disabled=es_tancat)
                    preg = st.text_input("Pregunta o necesidad:", value=br[5], key=f"preg_{br_id}", disabled=es_tancat)
                    passos = st.text_input("Próximos pasos:", value=br[6], key=f"passos_{br_id}", disabled=es_tancat)
                    if not es_tancat:
                        st.button("💾 Guardar Notes", key=f"save_{br_id}", type="primary", on_click=actualitzar_notes_br, args=(br_id, notes, preg, passos))
                
                st.write("<br>", unsafe_allow_html=True)

    if not es_tancat:
        st.markdown("---")
        if st.button("➕ Crear Nova Big Rock", type="primary"):
            st.session_state.mostrar_formulari_br = not st.session_state.mostrar_formulari_br

        if st.session_state.mostrar_formulari_br:
            with st.form("form_nova_br"):
                st.subheader("Configura la teva nova Big Rock")
                nou_nom = st.text_input("Títol de la Big Rock")
                c1, c2 = st.columns(2)
                persones = c1.text_input("Persones clau")
                reunions = c2.text_input("Reunions clau")
                st.markdown("#### TARs")
                t1, t2, t3, t4 = st.text_input("TAR 1"), st.text_input("TAR 2"), st.text_input("TAR 3"), st.text_input("TAR 4")
                
                if st.form_submit_button("Guardar", type="primary"):
                    if nou_nom:
                        c = run_query("INSERT INTO big_rocks (username, mes, nom, persones, reunions, notes_progres, pregunta, passos) VALUES (?, ?, ?, ?, ?, '', '', '')", (USUARI, MES, nou_nom, persones, reunions))
                        for i, desc_tar in enumerate([t1, t2, t3, t4]):
                            if desc_tar.strip():
                                run_query("INSERT INTO tars (id_br, num, descripcio, progres, estat) VALUES (?, ?, ?, ?, 'Actiu')", (c.lastrowid, f"TAR {i+1}", desc_tar, 0))
                        st.session_state.mostrar_formulari_br = False
                        st.rerun()

# ==========================================
# 5. PANTALLA DE RESUM (TANCAMENT)
# ==========================================
elif st.session_state.pantalla == 'resum':
    try:
        st.image("sorigue_logo_RGB-positivo.png", width=250)
    except:
        pass
        
    st.title(f"📊 Resum de Tancament - {MES}")
    
    brs = fetch_query("SELECT id, nom, persones, reunions FROM big_rocks WHERE username=? AND mes=?", (USUARI, MES))
    tars_completats, tars_pendents = [], []
    sumatori_progres, total_tars = 0, 0
    
    for br in brs:
        tars = fetch_query("SELECT descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu'", (br[0],))
        for t in tars:
            sumatori_progres += t[1]
            total_tars += 1
            if t[1] == 100: tars_completats.append(f"{br[1]} ➡️ {t[0]}")
            else: tars_pendents.append(f"{br[1]} ➡️ {t[0]} ({t[1]}%)")
    
    compliment_global = int(sumatori_progres / total_tars) if total_tars > 0 else 0
    
    progress_bar_colorida(compliment_global, is_global=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")
    ce, ct = st.columns(2)
    with ce:
        st.success(f"#### ✅ Èxits (100%)")
        for t in tars_completats: st.write(f"- {t}")
    with ct:
        st.warning(f"#### 🔄 Es traspassen")
        for t in tars_pendents: st.write(f"- {t}")
    st.markdown("---")

    def confirmar_tancament():
        run_query("INSERT OR IGNORE INTO mesos_tancats (username, mes) VALUES (?, ?)", (USUARI, MES))
        
        mesos = ["Gener", "Febrer", "Març", "Abril", "Maig", "Juny", "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"]
        parts = MES.split(" ")
        mes_actual_nom, any_actual = parts[0], int(parts[1])
        if mes_actual_nom in mesos:
            idx = mesos.index(mes_actual_nom)
            if idx == 11: nou_mes = f"Gener {any_actual + 1}"
            else: nou_mes = f"{mesos[idx+1]} {any_actual}"
        else:
            nou_mes = f"Mes_Següent {any_actual}"
            
        brs_actuals = fetch_query("SELECT id, nom, persones, reunions FROM big_rocks WHERE username=? AND mes=?", (USUARI, MES))
        for br in brs_actuals:
            tars_pendents_db = fetch_query("SELECT num, descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu' AND progres < 100", (br[0],))
            if tars_pendents_db:
                c = run_query("INSERT INTO big_rocks (username, mes, nom, persones, reunions, notes_progres, pregunta, passos) VALUES (?, ?, ?, ?, ?, '', '', '')", (USUARI, nou_mes, br[1], br[2], br[3]))
                for tar in tars_pendents_db:
                    run_query("INSERT INTO tars (id_br, num, descripcio, progres, estat) VALUES (?, ?, ?, ?, 'Actiu')", (c.lastrowid, tar[0], tar[1], tar[2]))
        
        st.session_state.mes_actual = nou_mes
        st.session_state.pantalla = 'dashboard'

    cb1, cb2 = st.columns(2)
    with cb1:
        st.button("⬅️ Cancel·lar", on_click=lambda: st.session_state.update(pantalla='dashboard'))
    with cb2:
        st.button("🔒 Confirmar Tancament i Crear Mes Següent", on_click=confirmar_tancament, type="primary", use_container_width=True)