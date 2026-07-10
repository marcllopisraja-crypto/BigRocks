import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Sistema Big Rocks", layout="wide", page_icon="🪨")

# ==========================================
# 1. CONFIGURACIÓ DE LA BASE DE DADES (SQLite)
# ==========================================
def init_db():
    conn = sqlite3.connect('bigrocks.db')
    c = conn.cursor()
    # Taula d'usuaris
    c.execute('''CREATE TABLE IF NOT EXISTS usuaris (
                    username TEXT PRIMARY KEY, 
                    password TEXT)''')
    # Taula de Big Rocks
    c.execute('''CREATE TABLE IF NOT EXISTS big_rocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    mes TEXT,
                    nom TEXT,
                    persones TEXT,
                    reunions TEXT,
                    notes_progres TEXT,
                    pregunta TEXT,
                    passos TEXT)''')
    # Taula de TARs
    c.execute('''CREATE TABLE IF NOT EXISTS tars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_br INTEGER,
                    num TEXT,
                    descripcio TEXT,
                    progres INTEGER,
                    estat TEXT,
                    FOREIGN KEY(id_br) REFERENCES big_rocks(id))''')
    conn.commit()
    conn.close()

init_db()

# --- Funcions auxiliars de BD ---
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

# ==========================================
# 2. SISTEMA DE LOGIN I REGISTRE
# ==========================================
if 'usuari_actual' not in st.session_state:
    st.session_state.usuari_actual = None

if st.session_state.usuari_actual is None:
    st.title("🔐 Accés a la Plataforma Big Rocks")
    
    tab1, tab2 = st.tabs(["Iniciar Sessió", "Registrar Nou Usuari"])
    
    with tab1:
        with st.form("login_form"):
            usuari = st.text_input("Nom d'usuari")
            contrasenya = st.text_input("Contrasenya", type="password")
            submit = st.form_submit_button("Entrar")
            
            if submit:
                result = fetch_query("SELECT * FROM usuaris WHERE username=? AND password=?", (usuari, contrasenya))
                if result:
                    st.session_state.usuari_actual = usuari
                    st.session_state.mes_actual = "Juliol 2026" # Mes per defecte en iniciar sessió
                    st.session_state.pantalla = 'dashboard'
                    st.rerun()
                else:
                    st.error("Usuari o contrasenya incorrectes.")
                    
    with tab2:
        with st.form("register_form"):
            nou_usuari = st.text_input("Nou nom d'usuari")
            nova_contra = st.text_input("Contrasenya", type="password")
            submit_reg = st.form_submit_button("Registrar")
            
            if submit_reg:
                try:
                    run_query("INSERT INTO usuaris (username, password) VALUES (?, ?)", (nou_usuari, nova_contra))
                    st.success("Usuari creat correctament! Ara pots iniciar sessió.")
                except sqlite3.IntegrityError:
                    st.error("Aquest nom d'usuari ja existeix.")
    st.stop() # Atura l'execució aquí si no està loguejat

# ==========================================
# 3. LÒGICA DE DADES DE L'USUARI
# ==========================================
# Variables de navegació
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = 'dashboard'
if 'mostrar_formulari_br' not in st.session_state:
    st.session_state.mostrar_formulari_br = False

USUARI = st.session_state.usuari_actual
MES = st.session_state.mes_actual

st.sidebar.write(f"👤 Connectat com: **{USUARI}**")
if st.sidebar.button("Tancar Sessió"):
    st.session_state.usuari_actual = None
    st.rerun()

st.sidebar.markdown("---")

# Funcions d'interacció amb SQLite
def actualitzar_progres_tar(id_tar, nou_progres):
    run_query("UPDATE tars SET progres=? WHERE id=?", (nou_progres, id_tar))

def actualitzar_text_tar(id_tar, nova_desc):
    run_query("UPDATE tars SET descripcio=? WHERE id=?", (nova_desc, id_tar))

def arxivar_tar(id_tar):
    run_query("UPDATE tars SET estat='Arxivat' WHERE id=?", (id_tar,))

def actualitzar_notes_br(id_br, notes, pregunta, passos):
    run_query("UPDATE big_rocks SET notes_progres=?, pregunta=?, passos=? WHERE id=?", (notes, pregunta, passos, id_br))

def crear_nova_br(nom, persones, reunions, nom_tars):
    c = run_query("INSERT INTO big_rocks (username, mes, nom, persones, reunions, notes_progres, pregunta, passos) VALUES (?, ?, ?, ?, ?, '', '', '')", 
                  (USUARI, MES, nom, persones, reunions))
    nou_id_br = c.lastrowid
    
    for i, desc_tar in enumerate(nom_tars):
        if desc_tar.strip() != "":
            run_query("INSERT INTO tars (id_br, num, descripcio, progres, estat) VALUES (?, ?, ?, ?, ?)", 
                      (nou_id_br, f"TAR {i+1}", desc_tar, 0, 'Actiu'))

def tancar_mes_db():
    # Definim quin serà el mes següent
    nou_mes = "Agost 2026" if "Juliol" in MES else "Setembre 2026"
    
    # Obtenim les Big Rocks actuals
    brs_actuals = fetch_query("SELECT id, nom, persones, reunions FROM big_rocks WHERE username=? AND mes=?", (USUARI, MES))
    
    for br in brs_actuals:
        id_br_antiga = br[0]
        # Mirem quins TARs estan actius i no completats
        tars_pendents = fetch_query("SELECT num, descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu' AND progres < 100", (id_br_antiga,))
        
        if tars_pendents:
            # Creem la nova Big Rock clonada pel mes següent
            c = run_query("INSERT INTO big_rocks (username, mes, nom, persones, reunions, notes_progres, pregunta, passos) VALUES (?, ?, ?, ?, ?, '', '', '')", 
                          (USUARI, nou_mes, br[1], br[2], br[3]))
            nou_id_br = c.lastrowid
            
            # Inserim els TARs pendents
            for tar in tars_pendents:
                run_query("INSERT INTO tars (id_br, num, descripcio, progres, estat) VALUES (?, ?, ?, ?, 'Actiu')", 
                          (nou_id_br, tar[0], tar[1], tar[2]))
                
    st.session_state.mes_actual = nou_mes
    st.session_state.pantalla = 'dashboard'

# ==========================================
# 4. PANTALLA 1: DASHBOARD PRINCIPAL
# ==========================================
if st.session_state.pantalla == 'dashboard':
    col_titol, col_boto = st.columns([3, 1])
    with col_titol:
        st.title("🪨 Dashboard Big Rocks")
        st.subheader(MES)
    with col_boto:
        st.write("<br>", unsafe_allow_html=True)
        st.button("📊 Avaluar i Tancar Mes", type="primary", use_container_width=True, on_click=lambda: st.session_state.update(pantalla='resum'))
    st.markdown("---")

    # Obtenir dades des de SQLite
    brs = fetch_query("SELECT id, nom, persones, reunions, notes_progres, pregunta, passos FROM big_rocks WHERE username=? AND mes=?", (USUARI, MES))

    if not brs:
        st.info("No hi ha cap Big Rock per a aquest mes. Afegeix-ne de noves a sota.")
    else:
        for br in brs:
            br_id = br[0]
            with st.container():
                st.markdown(f"## 🎯 {br[1]}")
                st.caption(f"👥 **Persones clau:** {br[2]} | 📅 **Reunions:** {br[3]}")
                
                # Obtenim els TARs actius
                tars = fetch_query("SELECT id, num, descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu'", (br_id,))
                
                progres_mitja = int(sum(t[3] for t in tars) / len(tars)) if tars else 0
                st.progress(progres_mitja / 100, text=f"Avenç global: {progres_mitja}%")
                st.markdown("---")
                
                for tar in tars:
                    tar_id, num, desc, progres = tar
                    col1, col2, col3, col4 = st.columns([1, 4, 3, 1])
                    with col1:
                        st.write(f"**{num}**")
                    with col2:
                        # Guardar descripció automàticament (usant on_change)
                        st.text_input("Desc", value=desc, key=f"desc_{tar_id}", label_visibility="collapsed", 
                                      on_change=actualitzar_text_tar, args=(tar_id, st.session_state.get(f"desc_{tar_id}", desc)))
                    with col3:
                        # Guardar progrés automàticament
                        st.slider("Progrés", min_value=0, max_value=100, value=progres, step=10, key=f"slider_{tar_id}", label_visibility="collapsed",
                                  on_change=actualitzar_progres_tar, args=(tar_id, st.session_state.get(f"slider_{tar_id}", progres)))
                    with col4:
                        st.button("🗑️", key=f"btn_{tar_id}", on_click=arxivar_tar, args=(tar_id,))
                
                # Notes i seguiment
                with st.expander("📝 Detalls, Preguntes i Pròxims Passos", expanded=False):
                    notes = st.text_area("Progreso:", value=br[4], key=f"notes_{br_id}")
                    preg = st.text_input("Pregunta o necesidad:", value=br[5], key=f"preg_{br_id}")
                    passos = st.text_input("Próximos pasos:", value=br[6], key=f"passos_{br_id}")
                    st.button("💾 Guardar Notes", key=f"save_{br_id}", on_click=actualitzar_notes_br, args=(br_id, notes, preg, passos))
                
                st.write("<br>", unsafe_allow_html=True)

    # CREAR NOVA BIG ROCK
    st.markdown("---")
    if st.button("➕ Crear Nova Big Rock"):
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
                    crear_nova_br(nou_nom, persones, reunions, [t1, t2, t3, t4])
                    st.session_state.mostrar_formulari_br = False
                    st.rerun()

# ==========================================
# 5. PANTALLA 2: RESUM DEL MES
# ==========================================
elif st.session_state.pantalla == 'resum':
    st.title(f"📊 Resum de Tancament - {MES}")
    
    brs = fetch_query("SELECT id, nom, persones, reunions FROM big_rocks WHERE username=? AND mes=?", (USUARI, MES))
    tars_completats, tars_pendents = [], []
    persones_set, reunions_set = set(), set()
    
    for br in brs:
        if br[2]: persones_set.add(br[2])
        if br[3]: reunions_set.add(br[3])
        
        tars = fetch_query("SELECT descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu'", (br[0],))
        for t in tars:
            if t[1] == 100:
                tars_completats.append(f"{br[1]} ➡️ {t[0]}")
            else:
                tars_pendents.append(f"{br[1]} ➡️ {t[0]} ({t[1]}%)")
                
    st.markdown("<br>", unsafe_allow_html=True)
    cp, cr = st.columns(2)
    with cp: st.info(f"### 👥 PERSONES CLAU\n" + "\n".join([f"- {p}" for p in persones_set if p]))
    with cr: st.info(f"### 📅 REUNIONS CLAU\n" + "\n".join([f"- {r}" for r in reunions_set if r]))
    
    st.markdown("---")
    ce, ct = st.columns(2)
    with ce:
        st.success("#### ✅ Èxits del mes")
        for t in tars_completats: st.write(f"- {t}")
    with ct:
        st.warning("#### 🔄 Es traspassen")
        for t in tars_pendents: st.write(f"- {t}")

    st.markdown("---")
    cb1, cb2 = st.columns(2)
    with cb1:
        st.button("⬅️ Cancel·lar", on_click=lambda: st.session_state.update(pantalla='dashboard'))
    with cb2:
        st.button("🚀 Confirmar i Crear Mes Següent", on_click=tancar_mes_db, type="primary", use_container_width=True)