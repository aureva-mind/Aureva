import os
import streamlit as st
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Aureva Mind", page_icon="🌙", layout="centered"
)

# --- STYLE CSS NUIT ÉTOILÉE & DESIGN ---
st.markdown(
    """
    <style>
    /* Fond général de l'application (Nuit étoilée) */
    .stApp {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 50%, #415a77 100%);
        color: #e0e1dd;
    }
    
    /* Titres et textes */
    h1, h2, h3, p, label, .stMarkdown {
        color: #f8f9fa !important;
    }

    /* Boutons standards (Orange) */
    .stButton>button {
        background: linear-gradient(135deg, #f4a261 0%, #e76f51 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 15px rgba(231, 111, 81, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(231, 111, 81, 0.6);
        background: linear-gradient(135deg, #f5b078 0%, #eb8267 100%);
    }

    /* Style spécifique pour les boutons d'engagement (Verts en relief) */
    div.stButton > button[kind="primary"], div.stButton > button.btn-vert {
        background: linear-gradient(135deg, #2a9d8f 0%, #21867a 100%) !important;
        box-shadow: 0 4px 15px rgba(42, 157, 143, 0.4) !important;
    }
    div.stButton > button[kind="primary"]:hover, div.stButton > button.btn-vert:hover {
        background: linear-gradient(135deg, #38b000 0%, #2b9348 100%) !important;
        box-shadow: 0 6px 20px rgba(56, 176, 0, 0.6) !important;
    }

    /* Champs de saisie et sélecteurs */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.07);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }
    
    /* Cartes d'alerte / info */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Configuration de la base de données SQLite
DB_FILE = "dreams.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
  __tablename__ = "users"
  id = Column(Integer, primary_key=True, index=True)
  first_name = Column(String, default="Thomas")
  is_premium = Column(Boolean, default=False)
  dreams_count = Column(Integer, default=2)


try:
  Base.metadata.create_all(bind=engine)
except Exception as e:
  pass

db = SessionLocal()
user = db.query(User).first()
if not user:
  user = User(first_name="Thomas", is_premium=False, dreams_count=2)
  db.add(user)
  db.commit()
  db.refresh(user)

# --- BARRE LATÉRALE : SÉLECTEUR DE LANGUE ---
with st.sidebar:
  st.markdown("### 🌐 Langue / Language")
  langue = st.selectbox(
      "Choisissez votre langue",
      ["🇫🇷 Français", "🇬🇧 English", "🇪🇸 Español", "🇩🇪 Deutsch", "🇮🇹 Italiano"],
  )
  st.markdown("---")
  st.write("✨ **Aureva Mind** — Édition Nuit Étoilée")

# Dictionnaires de traduction très légers pour l'interface
textes = {
    "🇫🇷 Français": {
        "titre": "🌙 Bonjour Thomas",
        "intro": (
            "Explorez les profondeurs de votre subconscient à travers une"
            " analyse onirique guidée par l'intelligence artificielle."
        ),
        "tab1": "✨ Nouveau Rêve",
        "tab2": "📜 Journal Intime",
        "tab3": "📊 Statistiques",
        "limite": (
            "⚠️ Thomas, vous avez atteint votre limite de 3 rêves gratuits."
        ),
        "choix_offre": (
            "Choisissez l'une de nos offres ci-dessous pour continuer à"
            " explorer vos rêves sans limite :"
        ),
        "btn_15": "🌿 15 Rêves — 4,99 €",
        "btn_illimite": "⭐ Illimité (1 an) — 12 €",
        "input_titre": "Titre du rêve (optionnel)",
        "emotion": "Émotion dominante au réveil",
        "lucidite": "Niveau de lucidité",
        "desc_reve": "Racontez votre rêve en détail...",
        "btn_analyser": "Analyser mon rêve",
        "succes_analyse": "Analyse terminée avec succès !",
        "interpretation": "🔮 Interprétation onirique",
        "journal_titre": "📜 Votre Journal Intime",
        "journal_desc": (
            "Retrouvez ici l'historique de vos rêves enregistrés et analysés."
        ),
        "stats_titre": "📊 Statistiques oniriques",
        "stats_desc": (
            "Visualisez l'évolution de vos émotions et de votre lucidité."
        ),
    },
    "🇬🇧 English": {
        "titre": "🌙 Hello Thomas",
        "intro": (
            "Explore the depths of your subconscious through AI-guided dream"
            " analysis."
        ),
        "tab1": "✨ New Dream",
        "tab2": "📜 Dream Diary",
        "tab3": "📊 Statistics",
        "limite": "⚠️ Thomas, you have reached your limit of 3 free dreams.",
        "choix_offre": (
            "Choose one of our offers below to continue exploring your dreams"
            " without limits:"
        ),
        "btn_15": "🌿 15 Dreams — €4.99",
        "btn_illimite": "⭐ Unlimited (1 year) — €12",
        "input_titre": "Dream title (optional)",
        "emotion": "Dominant emotion upon waking",
        "lucidite": "Level of lucidity",
        "desc_reve": "Tell your dream in detail...",
        "btn_analyser": "Analyze my dream",
        "succes_analyse": "Analysis successfully completed!",
        "interpretation": "🔮 Dream Interpretation",
        "journal_titre": "📜 Your Dream Diary",
        "journal_desc": "Find your recorded and analyzed dreams history here.",
        "stats_titre": "📊 Dream Statistics",
        "stats_desc": "Visualize the evolution of your emotions and lucidity.",
    },
}

# Langue par défaut en français si non trouvée
t = textes.get(langue, textes["🇫🇷 Français"])

# --- INTERFACE UTILISATEUR ---
st.markdown(f"<h1>{t['titre']}</h1>", unsafe_allow_html=True)
st.write(t["intro"])

# Onglets de navigation traduits
tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

with tab1:
  max_gratuits = 3
  if user.dreams_count >= max_gratuits and not user.is_premium:
    st.markdown(t["limite"])
    st.info(t["choix_offre"])

    # Boutons d'engagement en vert
    col1, col2 = st.columns(2)
    with col1:
      if st.button(t["btn_15"], type="primary"):
        user.dreams_count = max(0, user.dreams_count - 15)
        db.commit()
        st.success("Pack activé !")
        st.rerun()

    with col2:
      if st.button(t["btn_illimite"], type="primary"):
        user.is_premium = True
        db.commit()
        st.success("Abonnement activé !")
        st.rerun()

  else:
    st.write(f"💡 Rêves enregistrés : {user.dreams_count} / {max_gratuits}")

    titre_reve = st.text_input(t["input_titre"])
    emotion = st.selectbox(
        t["emotion"],
        ["Confus(e)", "Joyeux(se)", "Anxieux(se)", "Neutre", "Fasciné(e)"],
    )
    lucidite = st.slider(t["lucidite"], 1, 5, 3)
    description_reve = st.text_area(
        t["desc_reve"], placeholder="J'étais en train de..."
    )

    if st.button(t["btn_analyser"]):
      if not description_reve.strip():
        st.warning("Veuillez raconter votre rêve.")
      else:
        with st.spinner("Analyse..."):
          st.success(t["succes_analyse"])
          st.subheader(t["interpretation"])
          st.write(
              f"**Émotion :** {emotion} (Lucidité : {lucidite}/5)"
          )
          st.write(
              "Ce rêve met en lumière une réflexion active de votre"
              " subconscient."
          )

          user.dreams_count += 1
          db.commit()

with tab2:
  st.subheader(t["journal_titre"])
  st.write(t["journal_desc"])

with tab3:
  st.subheader(t["stats_titre"])
  st.write(t["stats_desc"])
