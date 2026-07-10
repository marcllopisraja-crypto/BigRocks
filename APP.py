import streamlit as st
import sqlite3
import pandas as pd

# ==========================================
# 0. CONFIGURACIÓ I DISSENY CORPORATIU
# ==========================================
st.set_page_config(page_title="BigRocks - Sorigué", layout="wide", page_icon="🪨")

st.markdown("""
    <style>
    /* NETEJA DE LA INTERFÍCIE - Mantenint la navegació intacta */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}

    /* Fons general suau */
    .stApp { background-color: #f8f9fa; }

    /* BARRA LATERAL BLAU CORPORATIU */
    [data-testid="stSidebar"] {
        background-color: #009FE3 !important;
    }
    
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: white !important;
    }

    [data-testid="stSidebar"] img {
        filter: brightness(0) invert(1);
    }

    /* Botons barra lateral */
    [data-testid="stSidebar"] button {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        color: white !important;
        border-radius: 8px;
    }

    /* TARGETES */
    div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }

    /* Botons principals */
    .stButton>button[kind="primary"] {
        background-color: #009FE3 !important;
        color: white !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. TRADUCCIONS
# ==========================================
TRANS = {
    'ca': {
        'login': "Accés a la Plataforma", 'usr': "Nom d'usuari", 'pwd': "Contrasenya", 'enter': "Entrar", 'reg': "Registrar",
        'err': "Usuari o contrasenya incorrectes.", 'conn': "Connectat com:", 'lang': "Idioma", 'nav': "Navegar mesos",
        'closed': "🔒 Mes TANCAT", 'open': "✏️ Mes Obert", 'logout': "Tancar Sessió", 'eval': "Avaluar i Tancar Mes",
        'no_br': "No hi ha cap BigRock. Afegeix-ne una.", 'ppl': "Persones:", 'meet': "Reunions:",
        'prog': "Assoliment global:", 'state': "Estat", 'desc': "Tasca", 'details': "Detalls", 'save': "Guardar",
        'create': "➕ Crear Nova", 'title': "Títol BigRock", 'sum': "Resum Tancament", 'succ': "Èxits (100%)",
        'trans': "Es traspassen", 'cancel': "Cancel·lar", 'confirm': "Confirmar i Crear Mes Següent",
        'months': ["Gener", "Febrer", "Març", "Abril", "Maig", "Juny", "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"]
    },
    'es': {
        'login': "Acceso a la Plataforma", 'usr': "Nombre de usuario", 'pwd': "Contraseña", 'enter': "Entrar", 'reg': "Registrar",
        'err': "Usuario o contraseña incorrectos.", 'conn': "Conectado como:", 'lang': "Idioma", 'nav': "Navegar meses",
        'closed': "🔒 Mes CERRADO", 'open': "✏️ Mes Abierto", 'logout': "Cerrar Sesión", 'eval': "Evaluar y Cerrar Mes",
        'no_br': "No hay BigRocks. Añade una.", 'ppl': "Personas:", 'meet': "Reuniones:",
        'prog': "Avance global:", 'state': "Estado", 'desc': "Tarea", 'details': "Detalles", 'save': "Guardar",
        'create': "➕ Crear Nueva", 'title': "Título BigRock", 'sum': "Resumen Cierre", 'succ': "Éxitos (100%)",
        'trans': "Se traspasan", 'cancel': "Cancelar", 'confirm': "Confirmar y Crear Mes Siguiente",
        'months': ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
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

# ==========================================
# 3. LOGIN
# ==========================================
if 'usuari_actual' not in st.session_state: st.session_state.usuari_actual = None

if st.session_state.usuari_actual is None:
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: st.image("sorigue_logo_RGB-positivo.png", width=250)
        except: st.title("Sorigué")
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Reg"])
        with tab1:
            with st.form("login"):
                u, p = st.text_input("User"), st.text_input("Pass", type="password")
                if st.form_submit_button("Entrar", type="primary"):
                    data = fetch_query("SELECT language FROM usuaris WHERE username=? AND password=?", (u, p))
                    if data:
                        st.session_state.usuari_actual = u
                        st.session_state.idioma = data[0][0]
                        st.session_state.mes_actual = "Juliol 2026" if st.session_state.idioma == 'ca' else "Julio 2026"
                        st.session_state.pantalla = 'dashboard'
                        st.rerun()
        with tab2:
            with st.form("reg"):
                u, p = st.text_input("User"), st.text_input("Pass", type="password")
                lang = st.selectbox("Idioma", ["ca", "es"], format_func=lambda x: "Català" if x=="ca" else "Español")
                if st.form_submit_button("Reg"):
                    run_query("INSERT INTO usuaris (username, password, language) VALUES (?, ?, ?)", (u, p, lang))
                    st.success("OK")
    st.stop()

# ==========================================
# 4. DASHBOARD
# ==========================================
USUARI = st.session_state.usuari_actual

try: st.sidebar.image("sorigue_logo_RGB-positivo.png", use_container_width=True)
except: st.sidebar.title("Sorigué")

if st.sidebar.button(t('logout')): st.session_state.usuari_actual=None; st.rerun()
idioma = st.sidebar.selectbox(t('lang'), ['ca', 'es'], index=0 if st.session_state.idioma=='ca' else 1, format_func=lambda x: "Català" if x=="ca" else "Español")
st.session_state.idioma = idioma

MES = st.sidebar.selectbox(t('nav'), [row[0] for row in fetch_query("SELECT DISTINCT mes FROM big_rocks WHERE username=?", (USUARI,))] or ["Juliol 2026"])
st.session_state.mes_actual = MES
es_tancat = len(fetch_query("SELECT * FROM mesos_tancats WHERE username=? AND mes=?", (USUARI, MES))) > 0

st.sidebar.markdown(t('closed') if es_tancat else t('open'))

st.title(f"BigRocks · {MES}")
brs = fetch_query("SELECT id, nom, persones, reunions FROM big_rocks WHERE username=? AND mes=?", (USUARI, MES))

for br in brs:
    st.subheader(f"🎯 {br[1]}")
    tars = fetch_query("SELECT id, num, descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu'", (br[0],))
    for tar in tars:
        c1, c2, c3 = st.columns([1, 4, 2])
        c1.write(tar[2])
        c2.text_input("Desc", value=tar[3], key=f"d{tar[0]}", disabled=es_tancat, on_change=lambda id=tar[0]: run_query("UPDATE tars SET descripcio=? WHERE id=?", (st.session_state[f"d{id}"], id)))
        c3.radio("Prog", [0, 50, 100], index=[0, 50, 100].index(tar[4]), horizontal=True, disabled=es_tancat, on_change=lambda id=tar[0]: run_query("UPDATE tars SET progres=? WHERE id=?", (st.session_state[f"r{id}"], id)), key=f"r{tar[0]}")

if not es_tancat and st.button(t('create')):
    run_query("INSERT INTO big_rocks (username, mes, nom) VALUES (?, ?, ?)", (USUARI, MES, "Nova BigRock"))
    st.rerun()

if not es_tancat and st.button(t('eval')):
    # Lógica de tancament segura
    tars_pendents = fetch_query("SELECT count(*) FROM tars t JOIN big_rocks b ON t.id_br = b.id WHERE b.mes=? AND t.progres < 100", (MES,))
    if tars_pendents[0][0] > 0:
        run_query("INSERT INTO mesos_tancats (username, mes) VALUES (?, ?)", (USUARI, MES))
        st.success("Mes tancat!")
        st.rerun()