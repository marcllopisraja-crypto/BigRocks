import streamlit as st
import sqlite3
import pandas as pd

# ==========================================
# 0. CONFIGURACIÓ I DISSENY (ESTIL SORIGUÉ)
# ==========================================
st.set_page_config(page_title="BigRocks - Sorigué", layout="wide", page_icon="🪨")

st.markdown("""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
    }

    /* Ocultar elements Streamlit sense perdre la navegació */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    
    /* Mantenir header però amagar icones sobrants */
    [data-testid="stHeader"] {background: transparent !important;}
    
    /* Barra Lateral Blau Sorigué (#009FE3) */
    [data-testid="stSidebar"] {
        background-color: #009FE3 !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] img { filter: brightness(0) invert(1); }

    /* Targetes */
    .stApp { background-color: #f8f9fa; }
    div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] {
        background-color: white;
        border-radius: 4px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }

    /* Botons Primaris (Blau Sorigué) */
    .stButton>button[kind="primary"] {
        background-color: #009FE3 !important;
        color: white !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. TRADUCCIONS I LÒGICA
# ==========================================
TRANS = {
    'ca': {
        'login_title': "Accés a la Plataforma", 'usr': "Usuari", 'pwd': "Contrasenya", 'enter': "Entrar", 'reg': "Registrar",
        'err': "Usuari o contrasenya incorrectes.", 'conn': "Connectat com:", 'lang': "Idioma", 'nav': "Navegar mesos",
        'closed': "🔒 Mes TANCAT", 'open': "✏️ Mes Obert", 'logout': "Tancar Sessió", 'eval': "Avaluar i Tancar",
        'no_br': "No hi ha cap BigRock.", 'ppl': "Persones:", 'meet': "Reunions:",
        'create': "➕ Crear Nova", 'title': "Títol BigRock", 'save': "Guardar", 'summary': "Resum Tancament",
        'successes': "Èxits (100%)", 'carry_over': "Es traspassen", 'cancel': "Cancel·lar", 
        'confirm': "Confirmar i Crear Mes Següent", 'already_exists': "El mes ja existeix!"
    },
    'es': {
        'login_title': "Acceso a la Plataforma", 'usr': "Usuario", 'pwd': "Contraseña", 'enter': "Entrar", 'reg': "Registrar",
        'err': "Usuario o contraseña incorrectos.", 'conn': "Conectado como:", 'lang': "Idioma", 'nav': "Navegar meses",
        'closed': "🔒 Mes CERRADO", 'open': "✏️ Mes Abierto", 'logout': "Cerrar Sesión", 'eval': "Evaluar y Cerrar",
        'no_br': "No hay ninguna BigRock.", 'ppl': "Personas:", 'meet': "Reuniones:",
        'create': "➕ Crear Nueva", 'title': "Título BigRock", 'save': "Guardar", 'summary': "Resumen Cierre",
        'successes': "Éxitos (100%)", 'carry_over': "Se traspasan", 'cancel': "Cancelar", 
        'confirm': "Confirmar y Crear Mes Siguiente", 'already_exists': "¡El mes ya existe!"
    }
}

def t(key):
    lang = st.session_state.get('idioma', 'ca')
    return TRANS[lang].get(key, key)

# ==========================================
# 2. BASE DE DADES
# ==========================================
def init_db():
    conn = sqlite3.connect('bigrocks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuaris (username TEXT PRIMARY KEY, password TEXT, language TEXT DEFAULT 'ca')''')
    c.execute('''CREATE TABLE IF NOT EXISTS big_rocks (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, mes TEXT, nom TEXT, persones TEXT, reunions TEXT, notes_progres TEXT, pregunta TEXT, passos TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tars (id INTEGER PRIMARY KEY AUTOINCREMENT, id_br INTEGER, num TEXT, descripcio TEXT, progres INTEGER, estat TEXT)''')
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

# ==========================================
# 3. LOGIN
# ==========================================
if 'usuari_actual' not in st.session_state: st.session_state.usuari_actual = None

if st.session_state.usuari_actual is None:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        try: st.image("sorigue_logo_RGB-positivo.png", width=250)
        except: st.title("Sorigué")
        tab1, tab2 = st.tabs(["Login", "Reg"])
        with tab1:
            with st.form("login"):
                u = st.text_input(t('usr'))
                p = st.text_input(t('pwd'), type="password")
                if st.form_submit_button(t('enter'), type="primary", use_container_width=True):
                    data = fetch_query("SELECT language FROM usuaris WHERE username=? AND password=?", (u, p))
                    if data:
                        st.session_state.usuari_actual = u
                        st.session_state.idioma = data[0][0]
                        st.session_state.mes_actual = "Juliol 2026"
                        st.session_state.pantalla = 'dashboard'
                        st.rerun()
        with tab2:
            with st.form("reg"):
                u = st.text_input(t('usr'))
                p = st.text_input(t('pwd'), type="password")
                l = st.selectbox("Idioma", ["ca", "es"], format_func=lambda x: "Català" if x=="ca" else "Español")
                if st.form_submit_button(t('reg'), type="primary", use_container_width=True):
                    run_query("INSERT INTO usuaris (username, password, language) VALUES (?, ?, ?)", (u, p, l))
                    st.success("OK")
    st.stop()

# ==========================================
# 4. DASHBOARD
# ==========================================
USUARI = st.session_state.usuari_actual
try: st.sidebar.image("sorigue_logo_RGB-positivo.png", use_container_width=True)
except: st.sidebar.title("Sorigué")

if st.sidebar.button(t('logout')): st.session_state.usuari_actual=None; st.rerun()
st.session_state.idioma = st.sidebar.selectbox(t('lang'), ['ca', 'es'], index=0 if st.session_state.idioma=='ca' else 1, format_func=lambda x: "Català" if x=="ca" else "Español")

MES = st.sidebar.selectbox(t('nav'), [row[0] for row in fetch_query("SELECT DISTINCT mes FROM big_rocks WHERE username=?", (USUARI,))] or ["Juliol 2026"])
st.session_state.mes_actual = MES
es_tancat = len(fetch_query("SELECT * FROM mesos_tancats WHERE username=? AND mes=?", (USUARI, MES))) > 0
st.sidebar.markdown(t('closed') if es_tancat else t('open'))

st.title(f"BigRocks · {MES}")
brs = fetch_query("SELECT id, nom, persones, reunions FROM big_rocks WHERE username=? AND mes=?", (USUARI, MES))

for br in brs:
    st.subheader(f"🎯 {br[1]}")
    tars = fetch_query("SELECT id, num, descripcio, progres FROM tars WHERE id_br=?", (br[0],))
    for tar in tars:
        c1, c2, c3 = st.columns([1, 4, 2])
        c1.write(tar[2])
        c2.text_input("Desc", value=tar[3], key=f"d{tar[0]}", disabled=es_tancat, on_change=lambda id=tar[0]: run_query("UPDATE tars SET descripcio=? WHERE id=?", (st.session_state[f"d{id}"], id)))
        c3.radio("Prog", [0, 50, 100], index=[0, 50, 100].index(tar[4]), horizontal=True, disabled=es_tancat, on_change=lambda id=tar[0]: run_query("UPDATE tars SET progres=? WHERE id=?", (st.session_state[f"r{id}"], id)), key=f"r{tar[0]}")

if not es_tancat and st.button(t('create')):
    run_query("INSERT INTO big_rocks (username, mes, nom) VALUES (?, ?, ?)", (USUARI, MES, "Nova BigRock"))
    st.rerun()

if not es_tancat and st.button(t('eval')):
    # Comprovar si el mes següent existeix per no duplicar
    existeix = fetch_query("SELECT * FROM big_rocks WHERE username=? AND mes=?", (USUARI, "Agost 2026"))
    if existeix:
        st.error(t('already_exists'))
    else:
        run_query("INSERT INTO mesos_tancats (username, mes) VALUES (?, ?)", (USUARI, MES))
        st.rerun()