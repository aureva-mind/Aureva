import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# ==========================================
# 1. DATABASE CONFIGURATION (SQLAlchemy)
# ==========================================
DATABASE_URL = "sqlite:///aureva_mind.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, unique=True, index=True)
    is_premium = Column(Boolean, default=False)
    premium_expiry = Column(DateTime, nullable=True)
    dreams = relationship("DreamModel", back_populates="owner", cascade="all, delete-orphan")

class DreamModel(Base):
    __tablename__ = "dreams"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    content = Column(Text, nullable=False)
    analysis = Column(Text, nullable=False)
    emotion = Column(String, default="Neutral")
    date = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    owner = relationship("User", back_populates="dreams")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_or_create_user(first_name: str):
    db = SessionLocal()
    try:
        clean_name = first_name.strip().capitalize() if first_name else "Voyager"
        user = db.query(User).filter(User.first_name == clean_name).first()
        if not user:
            user = User(first_name=clean_name, is_premium=False)
            db.add(user)
            db.commit()
            db.refresh(user)
        
        if user.is_premium and user.premium_expiry and datetime.now() > user.premium_expiry:
            user.is_premium = False
            db.commit()
            
        return user
    finally:
        db.close()

def save_dream(user_id: int, title: str, content: str, analysis: str, emotion: str):
    db = SessionLocal()
    try:
        db_dream = DreamModel(user_id=user_id, title=title, content=content, analysis=analysis, emotion=emotion)
        db.add(db_dream)
        db.commit()
    finally:
        db.close()

def delete_dream(dream_id: int):
    db = SessionLocal()
    try:
        dream = db.query(DreamModel).filter(DreamModel.id == dream_id).first()
        if dream:
            db.delete(dream)
            db.commit()
    finally:
        db.close()

def count_user_dreams(user_id: int) -> int:
    db = SessionLocal()
    try:
        return db.query(DreamModel).filter(DreamModel.user_id == user_id).count()
    finally:
        db.close()

def activate_annual_pass(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_premium = True
            user.premium_expiry = datetime.now() + timedelta(days=365)
            db.commit()
    finally:
        db.close()

# ==========================================
# 2. MULTILINGUAL DICTIONARY & AI ENGINE
# ==========================================
TRANSLATIONS = {
    "Français": {
        "title": "Aureva Mind",
        "subtitle": "Votre journal onirique annuel.",
        "name_input": "Votre prénom",
        "active_pass": "Édition Annuelle Active",
        "valid_until": "Accès complet valide jusqu'au :",
        "free_version": "Version Découverte (3 rêves max)",
        "pass_desc": "Offrez-vous une année complète d'explorations oniriques.",
        "pass_bullet1": "Rêves illimités pendant 1 an",
        "pass_bullet2": "Statistiques & tendances avancées",
        "pass_bullet3": "Analyses psychologiques profondes",
        "pass_cta": "Obtenir l'Édition Annuelle (9,99€)",
        "test_mode": "[Mode Test] Activer l'Édition Annuelle",
        "share_title": "Partager l'application",
        "share_link": "Lien de partage",
        "share_wa": "Partager sur WhatsApp",
        "share_tw": "Partager sur X / Twitter",
        "welcome": "Bonjour",
        "welcome_desc": "Explorez les profondeurs de votre subconscient à travers une analyse onirique guidée par l'intelligence artificielle.",
        "tab1": "✨ Nouveau Rêve",
        "tab2": "📜 Journal Intime",
        "tab3": "📊 Statistiques & Tendances",
        "limit_reached": "vous avez atteint votre limite de 3 rêves gratuits.",
        "limit_info": "Obtenez l'Édition Annuelle dans la barre latérale pour débloquer votre journal sans aucune limite.",
        "saved_count": "Rêves enregistrés :",
        "dream_title": "Titre du rêve (optionnel)",
        "emotion_label": "Émotion dominante au réveil",
        "lucidity_label": "Niveau de lucidité",
        "content_label": "Racontez votre rêve en détail...",
        "submit_btn": "Lancer l'analyse introspective",
        "success_save": "Rêve consigné dans votre journal !",
        "warning_empty": "Veuillez entrer le texte de votre rêve.",
        "journal_title": "Journal de",
        "empty_journal": "Votre journal est vide pour le moment.",
        "export_btn": "📥 Télécharger tout mon journal (CSV)",
        "delete_btn": "Supprimer ce rêve",
        "deleted_msg": "Rêve supprimé.",
        "locked_stats": "Les graphiques et bilans statistiques sont réservés aux détenteurs de l'Édition Annuelle.",
        "min_dreams_stats": "Enregistrez au moins 2 rêves pour afficher vos graphiques d'évolution.",
        "chart_title": "Évolution des rêves de",
        "emotions_list": ["Serein(e)", "Anxieux(se)", "Merveilleux(se)", "Confus(e)", "Euphorique", "Mélancolique", "Neutre"]
    },
    "English": {
        "title": "Aureva Mind",
        "subtitle": "Your annual dream journal.",
        "name_input": "Your first name",
        "active_pass": "Annual Edition Active",
        "valid_until": "Full access valid until:",
        "free_version": "Free Version (3 dreams max)",
        "pass_desc": "Treat yourself to a full year of dream exploration.",
        "pass_bullet1": "Unlimited dreams for 1 year",
        "pass_bullet2": "Advanced statistics & trends",
        "pass_bullet3": "Deep psychological analysis",
        "pass_cta": "Get Annual Edition (9.99€)",
        "test_mode": "[Test Mode] Enable Annual Pass",
        "share_title": "Share application",
        "share_link": "Share link",
        "share_wa": "Share on WhatsApp",
        "share_tw": "Share on X / Twitter",
        "welcome": "Hello",
        "welcome_desc": "Explore the depths of your subconscious through an AI-guided dream analysis.",
        "tab1": "✨ New Dream",
        "tab2": "📜 Dream Journal",
        "tab3": "📊 Statistics & Trends",
        "limit_reached": "you have reached your limit of 3 free dreams.",
        "limit_info": "Get the Annual Edition in the sidebar to unlock your journal without restrictions.",
        "saved_count": "Saved dreams:",
        "dream_title": "Dream title (optional)",
        "emotion_label": "Dominant emotion upon waking",
        "lucidity_label": "Lucidity level",
        "content_label": "Tell your dream in detail...",
        "submit_btn": "Run Introspective Analysis",
        "success_save": "Dream saved to your journal!",
        "warning_empty": "Please enter your dream text.",
        "journal_title": "Journal of",
        "empty_journal": "Your journal is empty for now.",
        "export_btn": "📥 Download my entire journal (CSV)",
        "delete_btn": "Delete this dream",
        "deleted_msg": "Dream deleted.",
        "locked_stats": "Charts and statistical reports are reserved for Annual Edition holders.",
        "min_dreams_stats": "Save at least 2 dreams to display your evolution charts.",
        "chart_title": "Dream evolution of",
        "emotions_list": ["Serene", "Anxious", "Wonderful", "Confused", "Euphoric", "Melancholic", "Neutral"]
    },
    "Español": {
        "title": "Aureva Mind",
        "subtitle": "Tu diario de sueños anual.",
        "name_input": "Tu nombre",
        "active_pass": "Edición Anual Activa",
        "valid_until": "Acceso completo válido hasta:",
        "free_version": "Versión Gratuita (3 sueños máx)",
        "pass_desc": "Regálate un año completo de exploración de sueños.",
        "pass_bullet1": "Sueños ilimitados por 1 año",
        "pass_bullet2": "Estadísticas y tendencias avanzadas",
        "pass_bullet3": "Análisis psicológico profundo",
        "pass_cta": "Obtener Edición Anual (9,99€)",
        "test_mode": "[Modo Prueba] Activar Pase Anual",
        "share_title": "Compartir aplicación",
        "share_link": "Enlace para compartir",
        "share_wa": "Compartir en WhatsApp",
        "share_tw": "Compartir en X / Twitter",
        "welcome": "Hola",
        "welcome_desc": "Explora las profundidades de tu subconsciente a través de un análisis de sueños guiado por IA.",
        "tab1": "✨ Nuevo Sueño",
        "tab2": "📜 Diario de Sueños",
        "tab3": "📊 Estadísticas y Tendencias",
        "limit_reached": "has alcanzado tu límite de 3 sueños gratuitos.",
        "limit_info": "Obtén la Edición Anual en la barra lateral para desbloquear tu diario sin restricciones.",
        "saved_count": "Sueños guardados:",
        "dream_title": "Título del sueño (opcional)",
        "emotion_label": "Emoción dominante al despertar",
        "lucidity_label": "Nivel de lucidez",
        "content_label": "Cuéntanos tu sueño en detalle...",
        "submit_btn": "Ejecutar Análisis Introspectivo",
        "success_save": "¡Sueño guardado en tu diario!",
        "warning_empty": "Por favor ingresa el texto de tu sueño.",
        "journal_title": "Diario de",
        "empty_journal": "Tu diario está vacío por ahora.",
        "export_btn": "📥 Descargar todo mi diario (CSV)",
        "delete_btn": "Eliminar este sueño",
        "deleted_msg": "Sueño eliminado.",
        "locked_stats": "Los gráficos y reportes estadísticos están reservados para la Edición Anual.",
        "min_dreams_stats": "Guarda al menos 2 sueños para mostrar tus gráficos de evolución.",
        "chart_title": "Evolución de los sueños de",
        "emotions_list": ["Sereno/a", "Ansioso/a", "Maravilloso/a", "Confuso/a", "Eufórico/a", "Melancólico/a", "Neutral"]
    }
}

def analyze_dream(content: str, emotion: str) -> str:
    content_lower = content.lower()
    theme = "Inner exploration"
    if "run" in content_lower or "chase" in content_lower or "escape" in content_lower or "courir" in content_lower or "huir" in content_lower:
        theme = "Pressure / Confrontation or avoidance"
    elif "fly" in content_lower or "sky" in content_lower or "air" in content_lower or "voler" in content_lower or "cielo" in content_lower:
        theme = "Desire for emancipation and freedom"
    elif "water" in content_lower or "sea" in content_lower or "ocean" in content_lower or "eau" in content_lower or "mar" in content_lower:
        theme = "Emotional depth and submerged unconscious"
    elif "fall" in content_lower or "falling" in content_lower or "tomber" in content_lower or "caer" in content_lower:
        theme = "Loss of bearings or need to let go"

    return f"""
    ### 🌌 Introspective & Oniric Synthesis
    * **Emotional dominance:** {emotion}
    * **Unconscious core theme:** _{theme}_
    
    ---
    
    #### 🔍 1. Symbol Decryption
    Your mind staged this narrative to express what daily words keep silent. The settings and actions reported reflect your subconscious attempt to resolve a tension or assimilate a recent shift.
    
    #### 🎭 2. Resonance with Daily Life
    The intensity felt upon waking suggests that a current situation mirrors this oniric pattern. Your analytical awareness sets aside signals that your night brings back to light.
    
    #### 💡 3. Personal Evolution Key
    *Ask yourself today:* What am I trying to escape, reach, or control in my waking life that resembles what I experienced in this dream?
    """.strip()

# ==========================================
# 3. STREAMLIT UI (Luxury & Multilingual)
# ==========================================
init_db()

st.set_page_config(
    page_title="Aureva Mind",
    page_icon="🌙",
    layout="centered"
)

# Sélecteur de langue dans la barre latérale en premier
st.sidebar.title("🌙 Aureva Mind")
selected_lang = st.sidebar.selectbox("🌐 Language / Langue / Idioma", ["Français", "English", "Español"])
t = TRANSLATIONS[selected_lang]

st.sidebar.caption(t["subtitle"])

first_name_input = st.sidebar.text_input(t["name_input"], value="Thomas")
user = get_or_create_user(first_name_input)

st.sidebar.markdown("---")

if user.is_premium:
    st.sidebar.success(f"✨ {t['active_pass']} ({user.first_name})")
    expiry_str = user.premium_expiry.strftime('%d/%m/%Y') if user.premium_expiry else "Unlimited"
    st.sidebar.caption(f"{t['valid_until']} {expiry_str}")
else:
    st.sidebar.warning(f"🔒 {t['free_version']}")
    st.sidebar.markdown(f"""
    📖 **Aureva Mind — Pass**
    *{t['pass_desc']}*
    * ♾️ {t['pass_bullet1']}
    * 📊 {t['pass_bullet2']}
    * 🧠 {t['pass_bullet3']}
    """)
    
    st.sidebar.markdown(
        f"[🚀 {t['pass_cta']}](https://buy.stripe.com/votre_lien_de_paiement)",
        unsafe_allow_html=True
    )
    
    if st.sidebar.button(f"⚡ {t['test_mode']}"):
        activate_annual_pass(user.id)
        st.success("Pass activated!")
        st.rerun()

# Partager l'application
st.sidebar.markdown("---")
st.sidebar.subheader(t["share_title"])
app_share_url = "https://aurevamind.streamlit.app"
st.sidebar.text_input(t["share_link"], value=app_share_url, label_visibility="collapsed")
st.sidebar.markdown(f"[💬 {t['share_wa']}](https://api.whatsapp.com/send?text={app_share_url})", unsafe_allow_html=True)

# Interface principale
st.title(f"🌙 {t['welcome']} {user.first_name}")
st.write(t["welcome_desc"])

tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

with tab1:
    dream_count = count_user_dreams(user.id)
    MAX_FREE = 3
    
    if not user.is_premium and dream_count >= MAX_FREE:
        st.error(f"⚠️ {user.first_name}, {t['limit_reached']}")
        st.info(t["limit_info"])
    else:
        if not user.is_premium:
            st.caption(f"💡 {t['saved_count']} {dream_count} / {MAX_FREE}")
            
        with st.form("dream_submission"):
            title = st.text_input(t["dream_title"])
            col1, col2 = st.columns(2)
            with col1:
                emotion = st.selectbox(t["emotion_label"], t["emotions_list"])
            with col2:
                lucidity = st.slider(t["lucidity_label"], 1, 5, 2)
                
            content = st.text_area(t["content_label"], height=180)
            submitted = st.form_submit_button(t["submit_btn"])
            
            if submitted:
                if content.strip():
                    with st.spinner("Analyzing..."):
                        analysis = analyze_dream(content, emotion)
                        final_title = title.strip() if title.strip() else f"Dream {datetime.now().strftime('%d/%m/%Y')}"
                        save_dream(user.id, final_title, content, analysis, emotion)
                    st.success(t["success_save"])
                    st.rerun()
                else:
                    st.warning(t["warning_empty"])

with tab2:
    st.subheader(f"📜 {t['journal_title']} {user.first_name}")
    db = SessionLocal()
    user_dreams = db.query(DreamModel).filter(DreamModel.user_id == user.id).all()
    db.close()
    
    if not user_dreams:
        st.info(t["empty_journal"])
    else:
        df_export = pd.DataFrame([{
            "Date": d.date,
            "Title": d.title,
            "Emotion": d.emotion,
            "Content": d.content,
            "Analysis": d.analysis
        } for d in user_dreams])
        
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=t["export_btn"],
            data=csv_data,
            file_name=f"aureva_mind_journal_{user.first_name.lower()}.csv",
            mime="text/csv",
        )
        st.divider()

        for dream in reversed(user_dreams):
            with st.expander(f"✨ {dream.title} — 📅 {dream.date} (Emotion: {dream.emotion})"):
                st.markdown(f"**📝 Narrative :**\n> {dream.content}")
                st.markdown(f"**🧠 AI Analysis :**\n{dream.analysis}")
                
                if st.button(t["delete_btn"], key=f"del_{dream.id}"):
                    delete_dream(dream.id)
                    st.success(t["deleted_msg"])
                    st.rerun()

with tab3:
    st.subheader("📊 Statistics")
    if not user.is_premium:
        st.warning(t["locked_stats"])
    else:
        db = SessionLocal()
        user_dreams = db.query(DreamModel).filter(DreamModel.user_id == user.id).all()
        db.close()
        
        if len(user_dreams) < 2:
            st.info(t["min_dreams_stats"])
        else:
            df = pd.DataFrame([{
                "Date": d.date,
                "Emotion": d.emotion,
                "Title": d.title
            } for d in user_dreams])
            
            fig = px.histogram(df, x="Emotion", color="Emotion", title=f"{t['chart_title']} {user.first_name}", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
