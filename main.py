import streamlit as st
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import plotly.graph_objects as go

def get_moon_phase_details(dt=None):
  """Calcule la phase lunaire et renvoie son nom, sa progression et sa signification."""
  if dt is None:
    dt = datetime.datetime.now()

  known_new_moon = datetime.datetime(2000, 1, 6, 18, 14)
  diff = dt - known_new_moon
  days = diff.total_seconds() / 86400
  cycles = days / 29.5305877057
  phase = cycles - int(cycles)  # Entre 0.0 et 1.0

  if phase < 0.03 or phase > 0.97:
    return (
        phase,
        "Nouvelle Lune 🌑",
        (
            "Intériorité profonde, silence du mental et semence des futurs"
            " projets oniriques."
        ),
    )
  elif phase < 0.22:
    return (
        phase,
        "Premier Croissant 🌒",
        (
            "Émergence de l'impulsion. Les rêves commencent à formuler des"
            " intentions claires."
        ),
    )
  elif phase < 0.28:
    return (
        phase,
        "Premier Quartier 🌓",
        (
            "Tension créatrice. Le subconscient reflète des choix conscients à"
            " opérer."
        ),
    )
  elif phase < 0.47:
    return (
        phase,
        "Gibbeuse Croissante 🌔",
        (
            "Affinement de l'intuition. L'esprit se prépare à une révélation"
            " majeure."
        ),
    )
  elif phase < 0.53:
    return (
        phase,
        "Pleine Lune 🌕",
        (
            "Apogée onirique ! Émotions, visions intenses et clarté à leur"
            " paroxysme."
        ),
    )
  elif phase < 0.72:
    return (
        phase,
        "Gibbeuse Décroissante 🌖",
        (
            "Temps d'intégration, de recul et d'analyse des messages perçus ces"
            " derniers jours."
        ),
    )
  elif phase < 0.78:
    return (
        phase,
        "Dernier Quartier 🌗",
        (
            "Phase de lâcher-prise. Nettoyage des vieux schémas psychologiques"
            " encombrants."
        ),
    )
  else:
    return (
        phase,
        "Dernier Croissant 🌘",
        (
            "Apaisement et repos de l'esprit avant l'amorce d'un nouveau"
            " cycle."
        ),
    )


def render_lunar_observatory():
    phase_val, phase_nom, signification = get_moon_phase_details()
    st.markdown("### 🌙 Observatoire de la Synchronodicité Lunaire")
    st.markdown(f"#### 🌙 Cycle Actuel : {phase_nom}")
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=phase_val * 100,
            number={
                "suffix": "%",
                "font": {"color": "#818cf8", "size": 28, "weight": "bold"}
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "#818cf8",
                }
            }
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e0e7ff"},
        height=220,
        margin=dict(t=20, b=10, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1e1b4b 0%, #17153b 100%);
            border: 1px solid #4338ca;
            border-radius: 14px;
            padding: 18px;
            color: #e0e7ff;
            margin-top: 10px;
            margin-bottom: 25px;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        ">
            <h4 style="margin: 0 0 8px 0; color: #818cf8; font-size: 1.1rem;">🔮 Clé Psychologique du Jour</h4>
            <p style="margin: 0 0 10px 0; font-size: 0.95rem; line-height: 1.5;"><b>Résonance onirique :</b> {signification}</p>
            <p style="margin: 0; font-style: italic; font-size: 0.85rem; color: #a5b4fc;">
            « En psychanalyse, la lune agit comme un miroir grossissant des profondeurs. Noter ton rêve sous cette influence permet de relier ton vécu intime aux grandes marées de l'inconscient. »
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- 1. CONFIGURATION DE LA PAGE & DESIGN NUIT ÉTOILÉE ---
st.set_page_config(
    page_title="Aureva Mind - Analyse de Rêves",
    page_icon="🌙",
    layout="wide"
)
render_lunar_observatory()

# Style CSS : Ciel étoilé dynamique, champs sombres avec texte blanc, et boutons Stripe corrigés
st.markdown("""
    <style>
    .stApp {
        background: 
            radial-gradient(2px 2px at 20px 30px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 40px 70px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 90px 40px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 160px 120px, #ffd700, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 200px 200px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 300px 80px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 450px 150px, #ffd700, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 500px 300px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 650px 70px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 750px 220px, #ffd700, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 850px 120px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 950px 280px, #ffffff, rgba(0,0,0,0)),
            linear-gradient(to bottom, #05070f, #1b1e3b, #05070f) !important;
        background-repeat: repeat;
        background-size: 500px 500px;
        color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0f111a !important;
    }
    h1, h2, h3, p, label, span, div {
        color: #f1f5f9 !important;
    }
    h1, h2, h3 {
    text-shadow: 0 2px 12px rgba(129, 140, 248, 0.4);
}
    /* Champs de saisie et textareas en mode sombre avec texte blanc */
    .stTextInput input, .stTextArea textarea {
        color: #ffffff !important;
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
    }
    /* Sélecteur (selectbox) en mode sombre */
    .stSelectbox [data-baseweb="select"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
    }
    .stSelectbox [data-baseweb="select"] * {
        color: #ffffff !important;
        background-color: #161b22 !important;
    }
    /* Listes déroulantes (popovers / listbox) en mode sombre */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"], div[role="listbox"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
    }
    div[data-baseweb="popover"] *, div[data-baseweb="menu"] *, ul[role="listbox"] *, div[role="listbox"] * {
        color: #ffffff !important;
        background-color: #161b22 !important;
    }
    div[data-baseweb="popover"] li[role="option"]:hover, div[data-baseweb="menu"] div[role="option"]:hover {
        background-color: #30363d !important;
        color: #ffffff !important;
    }
    /* Boîtes de résultats / alertes avec fond clair et écriture noire lisible */
    div[data-baseweb="notification"], .stAlert {
        background-color: #f8fafc !important;
        color: #0f111a !important;
        border: 1px solid #cbd5e1 !important;
    }
    .stAlert p, .stAlert span, .stAlert div, div[data-baseweb="notification"] p {
        color: #0f111a !important;
    }
    /* Boutons standards */
    .stButton>button {
        background: linear-gradient(to right, #4f46e5, #9333ea) !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
    }
    /* Boutons de liens Stripe (st.link_button) */
    a[data-testid="stLinkButton"], .stLinkButton a {
        background: linear-gradient(to right, #4f46e5, #9333ea) !important;
        color: #ffffff !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
        text-align: center !important;
    }
    a[data-testid="stLinkButton"] *, .stLinkButton a * {
        color: #ffffff !important;
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
    user = User(first_name="Thomas", is_premium=False, dreams_count=0)
    db.add(user)
    db.commit()
    db.refresh(user)

# --- 3. DICTIONNAIRE MULTILANGUE ---
translations = {
    "Français": {
        "welcome": "Bienvenue",
        "nav_analyze": "✨ Analyser",
        "nav_journal": "📖 Journal",
        "nav_stats": "📊 Stats",
        "nav_terms": "📜 CGU",
        "nav_account": "📝 Compte",
        "analysis_title": "✨ Nouvelle Analyse Onirique",
        "dream_title": "Titre de votre rêve",
        "dream_emotion": "Émotion principale",
        "dream_lucidity": "Niveau de lucidité (1 à 5)",
        "dream_desc": "Racontez votre rêve en détail (mots-clés, décors, actions)...",
        "btn_analyze": "Analyser mon rêve",
        "success_msg": "✨ Analyse onirique réalisée avec succès !",
        "interpretation_title": "Interprétation profonde pour",
        "empty_desc_warn": "Veuillez entrer la description de votre rêve avant de lancer l'analyse.",
        "journal_title": "📖 Journal de vos Rêves",
        "journal_desc": "Retrouvez l'historique complet et détaillé de vos analyses oniriques.",
        "no_dreams": "Aucun rêve enregistré pour le moment. Allez sur l'onglet 'Analyser' pour soumettre votre premier rêve !",
        "lucidity_label": "Niveau de lucidité",
        "story_label": "Récit",
        "stats_title": "📊 Statistiques & Statut",
        "stats_desc": "Suivez votre activité onirique en temps réel.",
        "total_dreams": "Total de rêves analysés",
        "status_premium": "⭐ Statut : Abonnement Illimité Actif",
        "status_free": "🌿 Statut : Compte Gratuit",
        "account_title": "📝 Espace Inscription & Gestion du Compte",
        "account_desc": "Gérez vos informations personnelles, votre abonnement et vos accès premium.",
        "terms_title": "📜 Conditions Générales d'Utilisation et de Vente (CGU / CGV)",
        "terms_text": """
### 1. Objet et Champ d'Application
Les présentes Conditions Générales d'Utilisation et de Vente (CGU/CGV) régissent l'accès et l'utilisation de la plateforme **Aureva Mind**, service numérique d'analyse et d'interprétation onirique. En utilisant l'application, l'utilisateur accepte sans réserve les présentes conditions.

### 2. Description des Services & Tarifs
Aureva Mind propose des services d'analyse psychologique et symbolique des rêves :
* **Pack 15 rêves** : Facturé 4,99 € (paiement unique, accès à 15 analyses détaillées).
* **Abonnement Illimité** : Facturé 12,00 € / mois (accès illimité aux analyses et fonctionnalités premium, sans engagement de durée).

### 3. Modalités de Paiement Sécurisé
Tous les paiements sont traités de manière sécurisée par notre partenaire financier **Stripe**. Aucune donnée bancaire sensible n'est stockée sur nos serveurs. L'accès aux services payants est effectif immédiatement après validation du paiement.

### 4. Résiliation et Remboursement
* **Abonnement** : L'abonnement mensuel est résiliable à tout moment directement depuis l'espace membre ou en contactant le support. La résiliation prend effet à la fin de la période de facturation en cours.
* **Droit de rétractation** : Conformément à la législation en vigueur sur les contenus numériques fournis sur support immatériel, l'exécution du service commence dès la validation de la commande, ce pour quoi l'utilisateur renonce expressément à son droit de rétractation après la première analyse réalisée.

### 5. Propriété Intellectuelle
L'ensemble des éléments, textes, algorithmes d'interprétation, codes sources et graphismes composant **Aureva Mind** sont protégés par le droit de la propriété intellectuelle. Toute reproduction ou exploitation non autorisée est strictement interdite.

### 6. Limitation de Responsabilité & Nature des Analyses
Les analyses oniriques fournies par Aureva Mind ont une vocation de développement personnel, de bien-être et de divertissement. Elles ne constituent en aucun cas un diagnostic médical, psychiatrique ou une thérapie clinique.
        """,
        "member_space": "⚙️ Espace Membre",
        "cancel_sub": "❌ Résilier l'abonnement",
        "manage_account": "📝 Inscription & Compte",
        "pack_btn": "✨ Pack 15 rêves (4,99 €)",
        "unlim_btn": "🚀 Illimité (12 €/mois)"
    },
    "English": {
        "welcome": "Welcome",
        "nav_analyze": "✨ Analyze",
        "nav_journal": "📖 Journal",
        "nav_stats": "📊 Stats",
        "nav_terms": "📜 T&C",
        "nav_account": "📝 Account",
        "analysis_title": "✨ New Dream Analysis",
        "dream_title": "Dream title",
        "dream_emotion": "Main emotion",
        "dream_lucidity": "Lucidity level (1 to 5)",
        "dream_desc": "Describe your dream in detail...",
        "btn_analyze": "Analyze my dream",
        "success_msg": "✨ Dream analysis completed successfully!",
        "interpretation_title": "Deep interpretation for",
        "empty_desc_warn": "Please enter your dream description before analyzing.",
        "journal_title": "📖 Dream Journal",
        "journal_desc": "Find your complete dream analysis history.",
        "no_dreams": "No dreams recorded yet. Go to 'Analyze' to submit your first dream!",
        "lucidity_label": "Lucidity level",
        "story_label": "Story",
        "stats_title": "📊 Statistics & Status",
        "stats_desc": "Track your dream activity in real time.",
        "total_dreams": "Total analyzed dreams",
        "status_premium": "⭐ Status: Unlimited Subscription Active",
        "status_free": "🌿 Status: Free Account",
        "account_title": "📝 Registration & Account Management",
        "account_desc": "Manage your personal info, subscription and premium access.",
        "terms_title": "📜 Terms and Conditions of Use and Sale (T&C)",
        "terms_text": "General terms and conditions of Aureva Mind.",
        "member_space": "⚙️ Member Space",
        "cancel_sub": "❌ Cancel subscription",
        "manage_account": "📝 Register / Account",
        "pack_btn": "✨ 15 Dreams Pack (€4.99)",
        "unlim_btn": "🚀 Unlimited (€12/month)"
    },
    "Español": {
        "welcome": "Bienvenido",
        "nav_analyze": "✨ Analizar",
        "nav_journal": "📖 Diario",
        "nav_stats": "📊 Stats",
        "nav_terms": "📜 Términos",
        "nav_account": "📝 Cuenta",
        "analysis_title": "✨ Nuevo Análisis Onírico",
        "dream_title": "Título de tu sueño",
        "dream_emotion": "Emoción principal",
        "dream_lucidity": "Nivel de lucidez (1 a 5)",
        "dream_desc": "Describe tu sueño en detalle...",
        "btn_analyze": "Analizar mi sueño",
        "success_msg": "✨ ¡Análisis completado!",
        "interpretation_title": "Interpretación profunda para",
        "empty_desc_warn": "Por favor ingresa la descripción.",
        "journal_title": "📖 Diario de Sueños",
        "journal_desc": "Historial de análisis.",
        "no_dreams": "No hay sueños registrados.",
        "lucidity_label": "Lucidez",
        "story_label": "Relato",
        "stats_title": "📊 Estadísticas y Estado",
        "stats_desc": "Sigue tu actividad.",
        "total_dreams": "Total de sueños",
        "status_premium": "⭐ Suscripción Ilimitada Activa",
        "status_free": "🌿 Cuenta Gratuita",
        "account_title": "📝 Registro y Cuenta",
        "account_desc": "Gestiona tu cuenta y suscripción.",
        "terms_title": "📜 Términos y Condiciones",
        "terms_text": "Términos del servicio.",
        "member_space": "⚙️ Miembros",
        "cancel_sub": "❌ Cancelar",
        "manage_account": "📝 Cuenta",
        "pack_btn": "✨ Pack 15 sueños (4,99 €)",
        "unlim_btn": "🚀 Ilimitado (12 €/mes)"
    },
    "Deutsch": {
        "welcome": "Willkommen",
        "nav_analyze": "✨ Analysieren",
        "nav_journal": "📖 Tagebuch",
        "nav_stats": "📊 Statistik",
        "nav_terms": "📜 AGB",
        "nav_account": "📝 Konto",
        "analysis_title": "✨ Neue Traumanalyse",
        "dream_title": "Traumtitel",
        "dream_emotion": "Hauptemotion",
        "dream_lucidity": "Klartraum-Level (1-5)",
        "dream_desc": "Beschreiben Sie Ihren Traum...",
        "btn_analyze": "Traum analysieren",
        "success_msg": "✨ Traumanalyse erfolgreich!",
        "interpretation_title": "Tiefenanalyse für",
        "empty_desc_warn": "Bitte Beschreibung eingeben.",
        "journal_title": "📖 Traumtagebuch",
        "journal_desc": "Ihre Traumanalysen.",
        "no_dreams": "Keine Träume.",
        "lucidity_label": "Klartraum-Level",
        "story_label": "Erzählung",
        "stats_title": "📊 Statistik & Status",
        "stats_desc": "Aktivität verfolgen.",
        "total_dreams": "Träume gesamt",
        "status_premium": "⭐ Abo aktiv",
        "status_free": "🌿 Kostenloses Konto",
        "account_title": "📝 Kontoverwaltung",
        "account_desc": "Verwalten Sie Ihr Konto.",
        "terms_title": "📜 AGB",
        "terms_text": "AGB von Aureva Mind.",
        "member_space": "⚙️ Bereich",
        "cancel_sub": "❌ Kündigen",
        "manage_account": "📝 Konto",
        "pack_btn": "✨ 15 Träume-Paket (4,99 €)",
        "unlim_btn": "🚀 Unbegrenzt (12 €/Monat)"
    },
    "Italiano": {
        "welcome": "Benvenuto",
        "nav_analyze": "✨ Analizza",
        "nav_journal": "📖 Diario",
        "nav_stats": "📊 Statistiche",
        "nav_terms": "📜 Termini",
        "nav_account": "📝 Account",
        "analysis_title": "✨ Nuova Analisi Onirica",
        "dream_title": "Titolo del sogno",
        "dream_emotion": "Emozione principale",
        "dream_lucidity": "Livello di lucidità (1-5)",
        "dream_desc": "Racconta il tuo sogno...",
        "btn_analyze": "Analizza il sogno",
        "success_msg": "✨ Analisi completata!",
        "interpretation_title": "Interpretazione per",
        "empty_desc_warn": "Inserisci la descrizione.",
        "journal_title": "📖 Diario dei Sogni",
        "journal_desc": "Cronologia.",
        "no_dreams": "Nessun sogno.",
        "lucidity_label": "Lucidità",
        "story_label": "Racconto",
        "stats_title": "📊 Statistiche e Stato",
        "stats_desc": "Monitora l'attività.",
        "total_dreams": "Sogni totali",
        "status_premium": "⭐ Abbonamento Illimitato Attivo",
        "status_free": "🌿 Account Gratuito",
        "account_title": "📝 Registrazione e Gestione Account",
        "account_desc": "Gestisci le tue informazioni.",
        "terms_title": "📜 Termini e Condizioni",
        "terms_text": "Termini di servizio di Aureva Mind.",
        "member_space": "⚙️ Area Membri",
        "cancel_sub": "❌ Annulla abbonamento",
        "manage_account": "📝 Account",
        "pack_btn": "✨ Pack 15 Sogni (€4.99)",
        "unlim_btn": "🚀 Illimitato (€12/mese)"
    }
}
