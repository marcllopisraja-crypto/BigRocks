import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema Big Rocks", layout="wide", page_icon="🪨")

st.title("🪨 Dashboard Big Rocks")

# 1. Variables d'estat inicials
if 'mes_actual' not in st.session_state:
    st.session_state.mes_actual = "Juliol 2026"

if 'mostrar_resum' not in st.session_state:
    st.session_state.mostrar_resum = False

st.subheader(st.session_state.mes_actual)

if 'big_rocks' not in st.session_state:
    st.session_state.big_rocks = [
        {
            "id": 1,
            "nom": "FACTURAR ABANS DE VACANCES",
            "persones": "Coordinadors",
            "reunions": "Coordinadors",
            "tars": [
                {"id_tar": 11, "num": "TAR 1", "desc": "Bimsa - Via Favència (277k€)", "progres": 40, "estat": "Actiu"},
                {"id_tar": 12, "num": "TAR 2", "desc": "Aura (141k€)", "progres": 100, "estat": "Actiu"},
                {"id_tar": 13, "num": "TAR 3", "desc": "Bimsa - Xavier Benguerel (66k€)", "progres": 0, "estat": "Actiu"},
                {"id_tar": 14, "num": "TAR 4", "desc": "Bimsa - Locals Entença (23k€)", "progres": 0, "estat": "Actiu"}
            ],
            "notes_progres": "He hecho reuniones con todos los implicados (Eloi, Marisol,...)",
            "pregunta": "Necesitamos un técnico responsable de RRHH central...",
            "passos": "Definir fechas y formaciones de operarios 2026."
        },
        {
            "id": 2,
            "nom": "REVISAR GEOS",
            "persones": "Montse + David D.",
            "reunions": "Montse + David D.",
            "tars": [
                {"id_tar": 21, "num": "TAR 1", "desc": "AMB Hotel Entitats", "progres": 30, "estat": "Actiu"},
                {"id_tar": 22, "num": "TAR 2", "desc": "Engestur Montcada", "progres": 10, "estat": "Actiu"},
                {"id_tar": 23, "num": "TAR 3", "desc": "Palamós", "progres": 0, "estat": "Actiu"}
            ],
            "notes_progres": "He hecho reuniones con todos los implicados...",
            "pregunta": "Preguntar a Paco sobre como está la incorporación...",
            "passos": "Programar 2das reuniones para concretar los avances."
        }
    ]

# Funcions de lògica interna
def arxivar_tar(br_id, tar_id):
    for br in st.session_state.big_rocks:
        if br['id'] == br_id:
            for tar in br['tars']:
                if tar['id_tar'] == tar_id:
                    tar['estat'] = "Arxivat"

def executar_traspas():
    noves_big_rocks = []
    
    # Filtrem què passa al mes següent
    for br in st.session_state.big_rocks:
        # Ens quedem només amb els TARs que estan Actius i a menys del 100%
        tars_pendents = [t for t in br['tars'] if t['estat'] == 'Actiu' and t['progres'] < 100]
        
        # Si la Big Rock encara té TARs pendents, la passem de mes
        if tars_pendents:
            nova_br = br.copy()
            nova_br['tars'] = tars_pendents
            nova_br['notes_progres'] = "" # Podem buidar les notes per començar el mes net
            nova_br['pregunta'] = ""
            nova_br['passos'] = ""
            noves_big_rocks.append(nova_br)
            
    # Actualitzem la memòria amb les dades netejades
    st.session_state.big_rocks = noves_big_rocks
    
    # Canviem el títol del mes
    st.session_state.mes_actual = "Agost 2026"
    
    # Tanquem el menú de resum
    st.session_state.mostrar_resum = False

# 2. Mostrar les Big Rocks a la pantalla
if not st.session_state.big_rocks:
    st.success("Totes les Big Rocks s'han completat! Felicitats. 🎉 Afegeix-ne de noves per a aquest mes.")
else:
    for br in st.session_state.big_rocks:
        with st.container():
            st.markdown(f"## 🎯 {br['nom']}")
            st.caption(f"👥 **Persones clau:** {br['persones']} | 📅 **Reunions:** {br['reunions']}")
            
            # Càlcul del progrés global de la Big Rock
            tars_actius = [t for t in br['tars'] if t['estat'] == 'Actiu']
            progres_mitja = int(sum(t['progres'] for t in tars_actius) / len(tars_actius)) if tars_actius else 0
            
            st.progress(progres_mitja / 100, text=f"Avenç global de la Big Rock: {progres_mitja}%")
            st.markdown("---")
            
            # Llistat dels TARs
            for tar in tars_actius:
                col1, col2, col3, col4 = st.columns([1, 4, 3, 1])
                
                with col1:
                    st.write(f"**{tar['num']}**")
                
                with col2:
                    tar['desc'] = st.text_input("Descripció del TAR", value=tar['desc'], key=f"desc_{tar['id_tar']}", label_visibility="collapsed")
                
                with col3:
                    tar['progres'] = st.slider(
                        "Progrés TAR", 
                        min_value=0, max_value=100, 
                        value=tar['progres'], 
                        step=10, 
                        key=f"slider_{tar['id_tar']}",
                        label_visibility="collapsed"
                    )
                
                with col4:
                    st.button("🗑️", key=f"btn_{tar['id_tar']}", on_click=arxivar_tar, args=(br['id'], tar['id_tar'],), help="Arxivar aquest TAR")
            
            # Camps finals de l'Excel
            with st.expander("📝 Detalls, Preguntes i Pròxims Passos", expanded=False):
                br['notes_progres'] = st.text_area("Progreso en esta Big Rock:", value=br['notes_progres'], key=f"prog_text_{br['id']}")
                br['pregunta'] = st.text_input("Pregunta o necesidad:", value=br['pregunta'], key=f"preg_{br['id']}")
                br['passos'] = st.text_input("Próximos pasos:", value=br['passos'], key=f"passos_{br['id']}")
            
            st.write("<br>", unsafe_allow_html=True)

# 3. Sidebar per Tancar el Mes
st.sidebar.title("Accions")

# Botó que obre/tanca el resum de tancament
def toggle_resum():
    st.session_state.mostrar_resum = not st.session_state.mostrar_resum

st.sidebar.button("Avaluar i Tancar Mes", type="primary", use_container_width=True, on_click=toggle_resum)

if st.session_state.mostrar_resum:
    st.sidebar.markdown("### Resum del traspàs al mes següent:")
    
    tars_que_passen = 0
    for br in st.session_state.big_rocks:
        tars_pendents = [t for t in br['tars'] if t['estat'] == 'Actiu' and t['progres'] < 100]
        if tars_pendents:
            st.sidebar.markdown(f"**{br['nom']}**")
            for t in tars_pendents:
                st.sidebar.caption(f"➡️ {t['num']}: {t['desc']} (Passa al {t['progres']}%)")
                tars_que_passen += 1
                
    if tars_que_passen == 0:
        st.sidebar.info("No hi ha cap TAR pendent per traspassar.")
        
    st.sidebar.markdown("---")
    # Aquest botó executa la funció real de neteja mitjançant `on_click`
    st.sidebar.button("Confirmar i Crear Mes Següent", on_click=executar_traspas, type="primary", use_container_width=True)