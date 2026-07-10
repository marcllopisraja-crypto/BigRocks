import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema Big Rocks", layout="wide", page_icon="🪨")

st.title("🪨 Dashboard Big Rocks")
st.subheader("Juliol 2026")

# 1. Base de dades inicial basada en el teu Excel "Big Rocks - Marc Llopis - Julio 2026.xlsx"
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

# Funció per arxivar un TAR
def arxivar_tar(br_id, tar_id):
    for br in st.session_state.big_rocks:
        if br['id'] == br_id:
            for tar in br['tars']:
                if tar['id_tar'] == tar_id:
                    tar['estat'] = "Arxivat"

# 2. Mostrar les Big Rocks a la pantalla
for br in st.session_state.big_rocks:
    with st.container():
        st.markdown(f"## 🎯 {br['nom']}")
        st.caption(f"👥 **Persones clau:** {br['persones']} | 📅 **Reunions:** {br['reunions']}")
        
        # Càlcul del progrés global de la Big Rock
        tars_actius = [t for t in br['tars'] if t['estat'] == 'Actiu']
        progres_mitja = int(sum(t['progres'] for t in tars_actius) / len(tars_actius)) if tars_actius else 0
        
        st.progress(progres_mitja / 100, text=f"Avenç global de la Big Rock: {progres_mitja}%")
        st.markdown("---")
        
        # Llistat dels TARs 1, 2, 3 i 4
        for tar in tars_actius:
            col1, col2, col3, col4 = st.columns([1, 4, 3, 1])
            
            with col1:
                st.write(f"**{tar['num']}**")
            
            with col2:
                # Camp de text per escriure en què consisteix el TAR (es pot editar al moment)
                tar['desc'] = st.text_input("Descripció del TAR", value=tar['desc'], key=f"desc_{tar['id_tar']}", label_visibility="collapsed")
            
            with col3:
                # Slider per marcar l'avenç del TAR concret
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
        with st.expander("📝 Detalls, Preguntes i Pròxims Passos", expanded=True):
            br['notes_progres'] = st.text_area("Progreso en esta Big Rock:", value=br['notes_progres'], key=f"prog_text_{br['id']}")
            br['pregunta'] = st.text_input("Pregunta o necesidad:", value=br['pregunta'], key=f"preg_{br['id']}")
            br['passos'] = st.text_input("Próximos pasos:", value=br['passos'], key=f"passos_{br['id']}")
        
        st.write("<br><br>", unsafe_allow_html=True)

# 3. Sidebar per Tancar el Mes
st.sidebar.title("Accions")
if st.sidebar.button("Avaluar i Tancar Mes", type="primary", use_container_width=True):
    st.sidebar.markdown("### Resum del traspàs a Agost:")
    for br in st.session_state.big_rocks:
        tars_pendents = [t for t in br['tars'] if t['estat'] == 'Actiu' and t['progres'] < 100]
        if tars_pendents:
            st.sidebar.write(f"**{br['nom']}**")
            for t in tars_pendents:
                st.sidebar.write(f" - {t['num']}: {t['desc']} (Passa al {t['progres']}%)")
    
    if st.sidebar.button("Crear Agost 2026"):
        st.sidebar.success("Mes creat! (Això es connectarà a la teva BD)")