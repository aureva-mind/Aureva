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
        "status_premium": "⭐ Abbonamento Attivo",
        "status_free": "🌿 Account Gratuito",
        "account_title": "📝 Gestione Account",
        "account_desc": "Gestisci il tuo profilo.",
        "terms_title": "📜 Termini e Condizioni",
        "terms_text": "Termini di servizio.",
        "member_space": "⚙️ Area",
        "cancel_sub": "❌ Annulla",
        "manage_account": "📝 Account",
        "pack_btn": "✨ Pacchetto 15 Sogni (4,99 €)",
        "unlim_btn": "🚀 Illimitato (12 €/mese)"
    },
    "Português": {
        "welcome": "Bem-vindo",
        "nav_analyze": "✨ Analisar",
        "nav_journal": "📖 Diário",
        "nav_stats": "📊 Stats",
        "nav_terms": "📜 Termos",
        "nav_account": "📝 Conta",
        "analysis_title": "✨ Nova Análise Onírica",
        "dream_title": "Título do sonho",
        "dream_emotion": "Emoção principal",
        "dream_lucidity": "Nível de lucidez",
        "dream_desc": "Descreva seu sonho...",
        "btn_analyze": "Analisar sonho",
        "success_msg": "✨ Análise concluída!",
        "interpretation_title": "Interpretação para",
        "empty_desc_warn": "Insira a descrição.",
        "journal_title": "📖 Diário de Sonhos",
        "journal_desc": "Histórico.",
        "no_dreams": "Nenhum sonho.",
        "lucidity_label": "Lucidez",
        "story_label": "Relato",
        "stats_title": "📊 Estatísticas",
        "stats_desc": "Acompanhe sua atividade.",
        "total_dreams": "Total de sonhos",
        "status_premium": "⭐ Assinatura Ativa",
        "status_free": "🌿 Conta Gratuita",
        "account_title": "📝 Gerenciamento de Conta",
        "account_desc": "Gerencie seus dados.",
        "terms_title": "📜 Termos e Condições",
        "terms_text": "Termos de uso.",
        "member_space": "⚙️ Membros",
        "cancel_sub": "❌ Cancelar",
        "manage_account": "📝 Conta",
        "pack_btn": "✨ Pacote 15 Sonhos (€4,99)",
        "unlim_btn": "🚀 Ilimitado (€12/mês)"
    },
    "Nederlands": {
        "welcome": "Welkom",
        "nav_analyze": "✨ Analyse",
        "nav_journal": "📖 Dagboek",
        "nav_stats": "📊 Stats",
        "nav_terms": "📜 Voorwaarden",
        "nav_account": "📝 Account",
        "analysis_title": "✨ Nieuwe Droomanalyse",
        "dream_title": "Droomtitel",
        "dream_emotion": "Belangrijkste emotie",
        "dream_lucidity": "Luciditeit",
        "dream_desc": "Beschrijf je droom...",
        "btn_analyze": "Analyseer droom",
        "success_msg": "✨ Analyse voltooid!",
        "interpretation_title": "Interpretatie voor",
        "empty_desc_warn": "Vul beschrijving in.",
        "journal_title": "📖 Droomdagboek",
        "journal_desc": "Geschiedenis.",
        "no_dreams": "Geen dromen.",
        "lucidity_label": "Luciditeit",
        "story_label": "Verhaal",
        "stats_title": "📊 Statistieken",
        "stats_desc": "Volg je activiteit.",
        "total_dreams": "Totaal dromen",
        "status_premium": "⭐ Abonnement Actief",
        "status_free": "🌿 Gratis Account",
        "account_title": "📝 Accountbeheer",
        "account_desc": "Beheer je account.",
        "terms_title": "📜 Algemene Voorwaarden",
        "terms_text": "Voorwaarden.",
        "member_space": "⚙️ Ruimte",
        "cancel_sub": "❌ Opzeggen",
        "manage_account": "📝 Account",
        "pack_btn": "✨ 15 Dromen Pakket (€4,99)",
        "unlim_btn": "🚀 Onbeperkt (€12/maand)"
    },
    "Polski": {
        "welcome": "Witaj",
        "nav_analyze": "✨ Analizuj",
        "nav_journal": "📖 Dziennik",
        "nav_stats": "📊 Statystyki",
        "nav_terms": "📜 Regulamin",
        "nav_account": "📝 Konto",
        "analysis_title": "✨ Nowa Analiza Snu",
        "dream_title": "Tytuł snu",
        "dream_emotion": "Główna emocja",
        "dream_lucidity": "Poziom świadomości",
        "dream_desc": "Opisz sen...",
        "btn_analyze": "Analizuj sen",
        "success_msg": "✨ Analiza zakończona!",
        "interpretation_title": "Interpretacja dla",
        "empty_desc_warn": "Wpisz opis.",
        "journal_title": "📖 Dziennik Snów",
        "journal_desc": "Historia.",
        "no_dreams": "Brak snów.",
        "lucidity_label": "Świadomość",
        "story_label": "Opis",
        "stats_title": "📊 Statystyki",
        "stats_desc": "Śledź aktywność.",
        "total_dreams": "Suma snów",
        "status_premium": "⭐ Subskrypcja aktywna",
        "status_free": "🌿 Konto darmowe",
        "account_title": "📝 Zarządzanie Kontem",
        "account_desc": "Zarządzaj swoim profilem.",
        "terms_title": "📜 Regulamin",
        "terms_text": "Regulamin serwisu.",
        "member_space": "⚙️ Strefa",
        "cancel_sub": "❌ Anuluj",
        "manage_account": "📝 Konto",
        "pack_btn": "✨ Pakiet 15 Snów (4,99 €)",
        "unlim_btn": "🚀 Nieograniczony (12 €/miesiąc)"
    },
    "Русский": {
        "welcome": "Добро пожаловать",
        "nav_analyze": "✨ Анализ",
        "nav_journal": "📖 Дневник",
        "nav_stats": "📊 Статистика",
        "nav_terms": "📜 Условия",
        "nav_account": "📝 Аккаунт",
        "analysis_title": "✨ Новый Анализ Сна",
        "dream_title": "Название сна",
        "dream_emotion": "Эмоция",
        "dream_lucidity": "Осознанность",
        "dream_desc": "Опишите сон...",
        "btn_analyze": "Анализировать сон",
        "success_msg": "✨ Успешно!",
        "interpretation_title": "Толкование для",
        "empty_desc_warn": "Введите описание.",
        "journal_title": "📖 Дневник снов",
        "journal_desc": "История.",
        "no_dreams": "Нет снов.",
        "lucidity_label": "Осознанность",
        "story_label": "Сон",
        "stats_title": "📊 Статистика",
        "stats_desc": "Активность.",
        "total_dreams": "Всего снов",
        "status_premium": "⭐ Подписка активна",
        "status_free": "🌿 Бесплатный аккаунт",
        "account_title": "📝 Управление Аккаунтом",
        "account_desc": "Управление профилем.",
        "terms_title": "📜 Условия",
        "terms_text": "Условия использования.",
        "member_space": "⚙️ Кабинет",
        "cancel_sub": "❌ Отменить",
        "manage_account": "📝 Аккаунт",
        "pack_btn": "✨ Пакет 15 снов (4,99 €)",
        "unlim_btn": "🚀 Безлимит (12 €/месяц)"
    },
    "日本語": {
        "welcome": "ようこそ",
        "nav_analyze": "✨ 分析",
        "nav_journal": "📖 ジャーナル",
        "nav_stats": "📊 統計",
        "nav_terms": "📜 規約",
        "nav_account": "📝 アカウント",
        "analysis_title": "✨ 新しい夢の分析",
        "dream_title": "夢のタイトル",
        "dream_emotion": "主な感情",
        "dream_lucidity": "明晰性",
        "dream_desc": "夢の詳細...",
        "btn_analyze": "夢を分析",
        "success_msg": "✨ 分析完了！",
        "interpretation_title": "解釈",
        "empty_desc_warn": "説明を入力してください。",
        "journal_title": "📖 夢のジャーナル",
        "journal_desc": "履歴。",
        "no_dreams": "記録なし。",
        "lucidity_label": "明晰性",
        "story_label": "内容",
        "stats_title": "📊 統計",
        "stats_desc": "活動の追跡。",
        "total_dreams": "夢の総数",
        "status_premium": "⭐ プレミアム有効",
        "status_free": "🌿 無料アカウント",
        "account_title": "📝 アカウント管理",
        "account_desc": "プロフィールの管理。",
        "terms_title": "📜 利用規約",
        "terms_text": "利用規約。",
        "member_space": "⚙️ スペース",
        "cancel_sub": "❌ 解約",
        "manage_account": "📝 アカウント",
        "pack_btn": "✨ 15夢パック (4.99 €)",
        "unlim_btn": "🚀 無制限 (12 €/月)"
    }
}

# --- 4. BARRE LATÉRALE (PROFIL & LANGUE) ---
with st.sidebar:
    st.markdown("### 👤 Mon Profil")
    nouveau_prenom = st.text_input("Votre prénom", value=user.first_name)
    if nouveau_prenom != user.first_name:
        user.first_name = nouveau_prenom
        db.commit()

    st.markdown("---")
    st.markdown("🌍 **Langue / Language**")
    langue = st.selectbox(
        "Choisissez votre langue", 
        ["Français", "English", "Español", "Deutsch", "Italiano", "Português", "Nederlands", "Polski", "Русский", "日本語"],
        label_visibility="collapsed"
    )
    t = translations[langue]

    st.markdown("---")
    st.subheader(t["member_space"])
    if user.is_premium:
        if st.button(t["cancel_sub"]):
            user.is_premium = False
            db.commit()
            st.rerun()
    else:
        st.info("💡 Mode gratuit actif.")

# --- 5. EN-TÊTE ---
st.title(f"Aureva Mind — {t['welcome']}, {user.first_name} 🌙")

# --- 6. VRAI MENU HORIZONTAL PAR ONGLETS (RESPONSIVE & ADAPTÉ MOBILE) ---
tab_analyze, tab_journal, tab_stats, tab_terms, tab_account = st.tabs([
    t["nav_analyze"], 
    t["nav_journal"], 
    t["nav_stats"], 
    t["nav_terms"],
    t["nav_account"]
])

# --- 7. ONGLET : ANALyser ---
with tab_analyze:
    st.subheader(t["analysis_title"])
    dream_title = st.text_input(t["dream_title"])
    dream_emotion = st.selectbox(t["dream_emotion"], ["Joie", "Peur", "Tristesse", "Mystère", "Aventure", "Autre"])
    dream_lucidity = st.slider(t["dream_lucidity"], 1, 5, 2)
    dream_desc = st.text_area(t["dream_desc"])

    if st.button(t["btn_analyze"]):
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

            st.success(t["success_msg"])
            st.markdown(f"### 🌌 {t['interpretation_title']} {user.first_name}")
            
            desc_lower = dream_desc.lower()
            symboles_analyses = []
            
            if any(w in desc_lower for w in ["eau", "mer", "océan", "inondation", "nager", "pluie", "rivière"]):
                symboles_analyses.append("🌊 **L'élément aquatique :** L'eau présente dans votre récit symbolise la profondeur de vos flux émotionnels et la manière dont vous gérez vos submersions intérieures.")
            if any(w in desc_lower for w in ["maison", "salon", "chambre", "porte", "fenêtre", "appartement", "toit"]):
                symboles_analyses.append("🏠 **Le décor architectural (Foyer) :** Révèle la structure intime de votre personnalité et la façon dont vous délimitez votre espace personnel et émotionnel.")
            if any(w in desc_lower for w in ["peur", "courir", "fuir", "danger", "poursuite", "cri"]):
                symboles_analyses.append("⚡ **La tension dynamique :** Met en lumière un défi en suspens dans votre vie éveillée qui réclame votre attention et un lâcher-prise salutaire.")
            if any(w in desc_lower for w in ["voler", "ciel", "hauteur", "chuter", "tomber", "monte"]):
                symboles_analyses.append("🕊️ **L'axe vertical (Élévation / Chute) :** Traduit votre quête inconsciente de liberté, de prise de recul ou, à l'inverse, une sensation temporaire de perte de repères.")
            
            if not symboles_analyses:
                symboles_analyses.append("🔍 **Analyse lexicale contextuelle :** Chaque tournure de phrase de votre récit cartographie avec précision vos aspirations actuelles et vos forces inconscientes.")
            
            bloc_symboles = "\n\n".join(symboles_analyses)

            analyse_approfondie = f"""
**1. Clé Émotionnelle & Fréquence de Fond**
Dominé par l'émotion de **{dream_emotion}**, ce songe agit comme un miroir puissant de votre équilibre psychologique actuel. Votre subconscient convertit vos tensions et désirs en une mise en scène hautement symbolique.

**2. Exploration Symbolique Détaillée (Mot par Mot)**
* *Votre récit intégral :* « {dream_desc} »
* *Décryptage approfondi :* 
{bloc_symboles}
L'agencement de ces mots dans votre description démontre une recherche active de résolution intérieure face aux questionnements qui traversent votre quotidien.

**3. Niveau de Lucidité ({dream_lucidity}/5)**
{'• **Conscience active :** Vous possédez une perception affûtée de vos mécanismes oniriques, ce qui dénote une excellente aptitude à reprendre le contrôle de vos choix de vie.' if dream_lucidity >= 3 else '• **Immersion intuitive profonde :** Votre esprit s\'est totalement abandonné au flux inconscient, captant des vérités et des intuitions brutes d\'une grande authenticité.'}

**4. Conseil Bien-être & Croissance Personnelle**
Accordez-vous un instant de calme pour assimiler ces messages. L'exploration de vos rêves est l'outil le plus direct pour cultiver une sérénité durable au quotidien.
            """
            st.info(analyse_approfondie)
        else:
            st.warning(t["empty_desc_warn"])

# --- 8. ONGLET : JOURNAL ---
with tab_journal:
    st.subheader(t["journal_title"])
    st.write(t["journal_desc"])
    st.markdown("---")

    tous_les_reves = db.query(DreamRecord).all()
    if not tous_les_reves:
        st.info(t["no_dreams"])
    else:
        for reve in reversed(tous_les_reves):
            with st.expander(f"🌙 {reve.title} — ({reve.emotion})"):
                st.write(f"**{t['lucidity_label']} :** {reve.lucidity}/5")
                st.write(f"**{t['story_label']} :** {reve.description}")

# --- 9. ONGLET : STATISTIQUES ---
with tab_stats:
    st.subheader(t["stats_title"])
    st.write(t["stats_desc"])
    st.markdown("---")
    st.metric(label=t["total_dreams"], value=user.dreams_count)
    if user.is_premium:
        st.success(t["status_premium"])
    else:
        st.info(t["status_free"])

# --- 10. ONGLET : CONDITIONS GÉNÉRALES ---
with tab_terms:
    st.subheader(t["terms_title"])
    st.markdown("---")
    st.markdown(t["terms_text"])

# --- 11. ONGLET : COMPTE & INSCRIPTION ---
with tab_account:
    st.subheader(t["account_title"])
    st.write(t["account_desc"])
    st.markdown("---")
    
    nouveau_prenom_tab = st.text_input("Modifier votre prénom", value=user.first_name, key="account_name_input")
    if nouveau_prenom_tab != user.first_name:
        user.first_name = nouveau_prenom_tab
        db.commit()
        st.success("Prénom mis à jour avec succès !")

    st.markdown("---")
    if user.is_premium:
        st.success("⭐ Vous bénéficiez actuellement de l'abonnement Illimité.")
        if st.button("❌ Résilier mon abonnement"):
            user.is_premium = False
            db.commit()
            st.rerun()
    else:
        st.info("🌿 Vous utilisez actuellement le compte gratuit.")
        if st.button("✨ Activer / Passer au compte membre"):
            user.is_premium = True
            db.commit()
            st.success("Compte membre activé avec succès !")
            st.rerun()

# --- 12. BOUTONS STRIPE PERMANENTS EN BAS DE PAGE ---
st.markdown("---")
st.markdown("### 🌙 Aureva Mind Premium")
st.write(translations[langue]["pack_btn"].split(" (")[0] + " & " + translations[langue]["unlim_btn"].split(" (")[0])
col1, col2 = st.columns(2)
with col1:
    st.link_button(translations[langue]["pack_btn"], "https://buy.stripe.com/9B68wQ9el5I21L1djxaIM00", use_container_width=True)
with col2:
    st.link_button(translations[langue]["unlim_btn"], "https://buy.stripe.com/fZu14o4Y53zUcpFenBaIM01", use_container_width=True)
