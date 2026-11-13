import os
import streamlit as st
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Aureva Mind", page_icon="🌙", layout="centered"
)

# --- STYLE CSS NUIT ÉTOILÉE & DESIGN CORRIGÉ ---
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

    /* Champs de saisie, sélecteurs et textareas : Texte bien blanc et lisible */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px;
    }
    
    /* Correction du placeholder (texte indicatif plus contrasté) */
    ::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
        opacity: 1;
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
  dreams_count = Column(Integer, default=0)


try:
  Base.metadata.create_all(bind=engine)
except Exception as e:
  pass

db = SessionLocal()
user = db.query(User).first()
if not user:
  user = User(first_name="Thomas", is_premium=False, dreams_count=0)
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

# Dictionnaires de traduction de l'interface
textes = {
    "🇫🇷 Français": {
        "titre": "🌙 Bonjour Thomas",
        "intro": (
            "Explorez les profondeurs de votre subconscient à travers une"
            " analyse onirique détaillée et guidée."
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
        "succes_analyse": "Analyse approfondie et détaillée terminée !",
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
            "Explore the depths of your subconscious through detailed"
            " AI-guided dream analysis."
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
        "succes_analyse": "Detailed analysis completed!",
        "journal_titre": "📜 Your Dream Diary",
        "journal_desc": "Find your recorded and analyzed dreams history here.",
        "stats_titre": "📊 Dream Statistics",
        "stats_desc": "Visualize the evolution of your emotions and lucidity.",
    },
}

t = textes.get(langue, textes["🇫🇷 Français"])

# --- INTERFACE UTILISATEUR ---
st.markdown(f"<h1>{t['titre']}</h1>", unsafe_allow_html=True)
st.write(t["intro"])

# Onglets de navigation
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
        st.success("Pack de 15 rêves activé !")
        st.rerun()

    with col2:
      if st.button(t["btn_illimite"], type="primary"):
        user.is_premium = True
        db.commit()
        st.success("Abonnement Annuel Illimité activé !")
        st.rerun()

  else:
    st.write(f"💡 Rêves enregistrés : {user.dreams_count} / {max_gratuits}")

    titre_reve = st.text_input(t["input_titre"])
    emotion = st.selectbox(
        t["emotion"],
        [
            "Confus(e)",
            "Joyeux(se)",
            "Anxieux(se)",
            "Neutre",
            "Fasciné(e)",
            "Apaisé(e)",
        ],
    )
    lucidite = st.slider(t["lucidite"], 1, 5, 3)
    description_reve = st.text_area(
        t["desc_reve"],
        placeholder="Ex: Je nageais dans la mer la nuit avec un ciel étoilé...",
    )

    if st.button(t["btn_analyser"]):
      if not description_reve.strip():
        st.warning("Veuillez raconter votre rêve avant de lancer l'analyse.")
      else:
        with st.spinner(
            "Exploration des profondeurs et analyse des mots-clés..."
        ):
          st.success(t["succes_analyse"])

          texte_lower = description_reve.lower()

          # Analyse détaillée avec détection de mots-clés dynamiques
          st.markdown("### 🔮 Analyse et Interprétation Profonde")

          st.markdown("#### 1. 🌊 Décodage de la symbolique & Mots-clés")
          symbolique_mots = []
          if "mer" in texte_lower or "eau" in texte_lower or "nager" in texte_lower:
            symbolique_mots.append(
                "**L'eau / La mer :** Symbolise vos émotions profondes, votre"
                " inconscient et votre capacité à naviguer à travers des"
                " périodes de grands changements émotionnels."
            )
          if "nuit" in texte_lower or "sombre" in texte_lower:
            symbolique_mots.append(
                "**La nuit :** Représente le mystère, l'inconnu et des aspects"
                " de vous-même encore cachés ou en phase de gestation."
            )
          if "ciel" in texte_lower or "étoile" in texte_lower:
            symbolique_mots.append(
                "**Le ciel / Les étoiles :** Indiquent une quête de sens,"
                " d'inspiration spirituelle et une connexion avec vos"
                " aspirations les plus hautes."
            )
          
          if not symbolique_mots:
            symbolique_mots.append(
                f"**Éléments clés de votre récit :** Votre description met en"
                " avant des dynamiques personnelles uniques qui traduisent"
                " votre état d'esprit actuel."
            )

          for sm in symbolique_mots:
            st.write(sm)

          st.markdown("#### 2. 🧠 Clé psychologique")
          st.write(
              f"Associée à l'émotion dominante de **{emotion}** et à un niveau"
              f" de lucidité de **{lucidite}/5**, cette expérience onirique"
              " révèle un travail de synthèse de votre esprit. Vous cherchez à"
              " faire la paix avec vos ressentis tout en gardant le cap sur vos"
              " objectifs profonds."
          )

          st.markdown("#### 3. 🌱 Conseil de votre subconscient")
          st.write(
              "Restez à l'écoute de votre intuition dans les jours à venir."
              " Votre subconscient vous invite à embrasser votre créativité et"
              " à accueillir vos émotions avec sérénité."
          )

          user.dreams_count += 1
          db.commit()

with tab2:
  st.subheader(t["journal_titre"])
  st.write(t["journal_desc"])

with tab3:
  st.subheader(t["stats_titre"])
  st.write(t["stats_desc"])
