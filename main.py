import streamlit as st
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- 1. CONFIGURATION DE LA PAGE & DESIGN NUIT ÉTOILÉE ---
st.set_page_config(
    page_title="Aureva Mind - Analyse de Rêves",
    page_icon="🌙",
    layout="wide"
)

# Style CSS personnalisé (Nuit étoilée & élégance)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #090a0f, #1b1e3b, #090a0f);
        color: #e2e8f0;
    }
    .sidebar .stSidebar {
        background-color: #0f111a;
    }
    h1, h2, h3 {
        color: #f1f5f9 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. BASE DE DONNÉES & GESTION UTILISATEUR ---
Base = declarative_base()
engine = create_engine('sqlite:///dreams.db', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    is_premium = Column(Boolean, default=False)
    dreams_count = Column(Integer, default=0)

class DreamRecord(Base):
    __tablename__ = 'dream_records'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    emotion = Column(String)
    lucidity = Column(Integer)
    description = Column(String)

try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

db = SessionLocal()
user = db.query(User).first()
if not user:
    user = User(first_name="Voyageur", is_premium=False, dreams_count=0)
    db.add(user)
    db.commit()
    db.refresh(user)

# --- 3. DICTIONNAIRE DE TRADUCTION ---
translations = {
    "Français": {
        "nav_title": "Navigation",
        "nav_space": "Mon Espace",
        "nav_analyze": "Analyser un rêve",
        "nav_terms": "Conditions Générales",
        "profile_title": "👤 Mon Profil",
        "profile_name": "Votre prénom",
        "lang_title": "🌍 Langue / Language",
        "lang_select": "Choisissez votre langue",
        "journal_titre": "📖 Journal de vos Rêves",
        "journal_desc": "Retrouvez l'historique de vos analyses oniriques.",
        "stats_titre": "📊 Statistiques & Statut",
        "stats_desc": "Suivez votre activité onirique.",
        "analysis_title": "✨ Nouvelle Analyse Onirique",
        "terms_title": "📜 Conditions Générales d'Utilisation et de Vente",
    },
    "English": {
        "nav_title": "Navigation",
        "nav_space": "My Space",
        "nav_analyze": "Analyze a dream",
        "nav_terms": "Terms & Conditions",
        "profile_title": "👤 My Profile",
        "profile_name": "Your first name",
        "lang_title": "🌍 Language",
        "lang_select": "Choose your language",
        "journal_titre": "📖 Dream Journal",
        "journal_desc": "Find your dream analysis history.",
        "stats_titre": "📊 Statistics & Status",
        "stats_desc": "Track your dream activity.",
        "analysis_title": "✨ New Dream Analysis",
        "terms_title": "📜 Terms and Conditions of Use and Sale",
    }
}

# --- 4. BARRE LATÉRALE (PROFIL, LANGUE, NAVIGATION & PAIEMENT) ---
with st.sidebar:
    st.markdown("### 👤 Mon Profil")
    nouveau_prenom = st.text_input("Votre prénom", value=user.first_name)
    if nouveau_prenom != user.first_name:
        user.first_name = nouveau_prenom
        db.commit()

    st.markdown("---")
    st.markdown("🌍 **Langue / Language**")
    langue = st.selectbox("Choisissez votre langue", ["Français", "English"])
    t = translations[langue]

    st.markdown("---")
    st.title(t["nav_title"])
    page = st.radio("Aller à", [t["nav_space"], t["nav_analyze"], t["nav_terms"]])

    # Section d'inscription / Gestion abonnement dans la sidebar
    st.markdown("---")
    st.subheader("⚙️ Espace Membre")
    if user.is_premium:
        if st.button("❌ Résilier l'abonnement"):
            user.is_premium = False
            db.commit()
            st.rerun()
    else:
        if st.button("📝 S'inscrire / Gérer mon compte"):
            st.info("Mode inscription / connexion actif.")

    # --- SECTION TOUJOURS VISIBLE EN BAS DE LA BARRE LATÉRALE (STRIPE) ---
    st.markdown("---")
    st.subheader("🌙 Aureva Mind Premium")
    st.write("Débloquez tout le potentiel de vos rêves :")

    st.link_button("✨ Pack 15 rêves (4,99 €)", "https://buy.stripe.com/9B68wQ9el5I21L1djxaIM00", use_container_width=True)
    st.link_button("🚀 Illimité (12 €/mois)", "https://buy.stripe.com/fZu14o4Y53zUcpFenBaIM01", use_container_width=True)

# --- 5. CORPS PRINCIPAL DE L'APPLICATION ---
if page == t["nav_space"]:
    st.title(f"Bienvenue, {user.first_name} 🌙")
    
    tab1, tab2, tab3 = st.tabs(["✨ Analyse IA", "📖 Journal", "📊 Statistiques"])
    
    with tab1:
        st.subheader(t["analysis_title"])
        dream_title = st.text_input("Titre de votre rêve")
        dream_emotion = st.selectbox("Émotion principale", ["Joie", "Peur", "Tristesse", "Mystère", "Aventure", "Autre"])
        dream_lucidity = st.slider("Niveau de lucidité (1 à 5)", 1, 5, 2)
        dream_desc = st.text_area("Racontez votre rêve en détail...")

        if st.button("Analyser mon rêve avec l'IA"):
            if dream_desc.strip():
                nouveau_reve = DreamRecord(
                    title=dream_title if dream_title else "Rêve sans titre",
                    emotion=dream_emotion,
                    lucidity=dream_lucidity,
                    description=dream_desc
                )
                db.add(nouveau_reve)
                user.dreams_count += 1
                db.commit()

                st.success("✨ Analyse onirique terminée avec succès !")
                st.markdown(f"### Interprétation pour {user.first_name}")
                st.info(f"Votre rêve évoque une forte énergie de type **{dream_emotion}**. Avec un niveau de lucidité de {dream_lucidity}/5, votre subconscient explore des pistes fascinantes.")
            else:
                st.warning("Veuillez entrer la description de votre rêve avant de lancer l'analyse.")

    with tab2:
        st.subheader(t["journal_titre"])
        st.write(t["journal_desc"])
        st.markdown("---")

        tous_les_reves = db.query(DreamRecord).all()
        if not tous_les_reves:
            st.info("Aucun rêve enregistré pour le moment. Analysez votre premier rêve !")
        else:
            for reve in reversed(tous_les_reves):
                with st.expander(f"🌙 {reve.title} — ({reve.emotion})"):
                    st.write(f"**Niveau de lucidité :** {reve.lucidity}/5")
                    st.write(f"**Récit :** {reve.description}")

    with tab3:
        st.subheader(t["stats_titre"])
        st.write(t["stats_desc"])
        st.markdown("---")
        st.metric(label="Total de rêves analysés", value=user.dreams_count)
        if user.is_premium:
            st.success("⭐ Statut : Abonnement Illimité Actif")
        else:
            st.info("🌿 Statut : Compte Gratuit")

elif page == t["nav_analyze"]:
    st.title("Espace d'analyse rapide")
    st.write("Rendez-vous dans l'onglet 'Mon Espace > Analyse IA' pour soumettre votre rêve.")

elif page == t["nav_terms"]:
    st.title(t["terms_title"])
    st.markdown("---")
    st.info("🚧 Section en cours de rédaction. Les mentions légales et conditions d'utilisation complètes seront ajoutées prochainement.")
    st.markdown("""
    ### 1. Objet
    Les présentes conditions générales régissent l'utilisation du service **Aureva Mind**.
    
    ### 2. Services et Tarifs
    * **Pack 15 rêves** : 4,99 € (paiement unique)
    * **Abonnement Illimité** : 12,00 € / mois (résiliable à tout moment depuis l'espace membre)
    """)
