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
    /* Correction absolue pour les boutons de liens Stripe (st.link_button) */
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

# --- 3. DICTIONNAIRE MULTILANGUE COMPLET (10 LANGUES) ---
translations = {
    "Français": {
        "welcome": "Bienvenue",
        "nav_analyze": "✨ Analyser un rêve",
        "nav_journal": "📖 Journal",
        "nav_stats": "📊 Statistiques",
        "nav_terms": "📜 Conditions Générales",
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
        "terms_title": "📜 Conditions Générales d'Utilisation et de Vente",
        "terms_text": "### 1. Objet\nLes présentes conditions générales régissent l'utilisation du service **Aureva Mind**.\n\n### 2. Services et Tarifs\n* **Pack 15 rêves** : 4,99 € (paiement unique)\n* **Abonnement Illimité** : 12,00 € / mois (résiliable à tout moment depuis l'espace membre)\n\n### 3. Propriété intellectuelle\nTous les contenus, analyses et visuels de l'application sont protégés.",
        "member_space": "⚙️ Espace Membre",
        "cancel_sub": "❌ Résilier l'abonnement",
        "manage_account": "📝 S'inscrire / Gérer mon compte",
        "pack_btn": "✨ Pack 15 rêves (4,99 €)",
        "unlim_btn": "🚀 Illimité (12 €/mois)"
    },
    "English": {
        "welcome": "Welcome",
        "nav_analyze": "✨ Analyze Dream",
        "nav_journal": "📖 Journal",
        "nav_stats": "📊 Statistics",
        "nav_terms": "📜 Terms & Conditions",
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
        "terms_title": "📜 Terms and Conditions of Use and Sale",
        "terms_text": "### 1. Object\nThese general conditions govern the use of the **Aureva Mind** service.\n\n### 2. Services and Pricing\n* **15 Dreams Pack**: €4.99 (one-time)\n* **Unlimited Subscription**: €12.00 / month",
        "member_space": "⚙️ Member Space",
        "cancel_sub": "❌ Cancel subscription",
        "manage_account": "📝 Register / Manage account",
        "pack_btn": "✨ 15 Dreams Pack (€4.99)",
        "unlim_btn": "🚀 Unlimited (€12/month)"
    },
    "Español": {
        "welcome": "Bienvenido",
        "nav_analyze": "✨ Analizar sueño",
        "nav_journal": "📖 Diario",
        "nav_stats": "📊 Estadísticas",
        "nav_terms": "📜 Términos",
        "analysis_title": "✨ Nuevo Análisis Onírico",
        "dream_title": "Título de tu sueño",
        "dream_emotion": "Emoción principal",
        "dream_lucidity": "Nivel de lucidez (1 a 5)",
        "dream_desc": "Describe tu sueño en detalle...",
        "btn_analyze": "Analizar mi sueño",
        "success_msg": "✨ ¡Análisis completado con éxito!",
        "interpretation_title": "Interpretación profunda para",
        "empty_desc_warn": "Por favor ingresa la descripción de tu sueño.",
        "journal_title": "📖 Diario de Sueños",
        "journal_desc": "Encuentra el historial de tus análisis.",
        "no_dreams": "No hay sueños registrados.",
        "lucidity_label": "Nivel de lucidez",
        "story_label": "Relato",
        "stats_title": "📊 Estadísticas y Estado",
        "stats_desc": "Sigue tu actividad onírica.",
        "total_dreams": "Total de sueños analizados",
        "status_premium": "⭐ Estado: Suscripción Ilimitada Activa",
        "status_free": "🌿 Estado: Cuenta Gratuita",
        "terms_title": "📜 Términos y Condiciones",
        "terms_text": "Condiciones generales del servicio Aureva Mind.",
        "member_space": "⚙️ Zona de Miembros",
        "cancel_sub": "❌ Cancelar suscripción",
        "manage_account": "📝 Registrarse",
        "pack_btn": "✨ Pack 15 sueños (4,99 €)",
        "unlim_btn": "🚀 Ilimitado (12 €/mes)"
    },
    "Deutsch": {
        "welcome": "Willkommen",
        "nav_analyze": "✨ Traum analysieren",
        "nav_journal": "📖 Tagebuch",
        "nav_stats": "📊 Statistik",
        "nav_terms": "📜 AGB",
        "analysis_title": "✨ Neue Traumanalyse",
        "dream_title": "Traumtitel",
        "dream_emotion": "Hauptemotion",
        "dream_lucidity": "Klartraum-Level (1-5)",
        "dream_desc": "Beschreiben Sie Ihren Traum...",
        "btn_analyze": "Meinen Traum analysieren",
        "success_msg": "✨ Traumanalyse erfolgreich abgeschlossen!",
        "interpretation_title": "Tiefenanalyse für",
        "empty_desc_warn": "Bitte geben Sie eine Beschreibung ein.",
        "journal_title": "📖 Traumtagebuch",
        "journal_desc": "Ihre Traumanalysen im Überblick.",
        "no_dreams": "Noch keine Träume gespeichert.",
        "lucidity_label": "Klartraum-Level",
        "story_label": "Erzählung",
        "stats_title": "📊 Statistik & Status",
        "stats_desc": "Verfolgen Sie Ihre Traumaktivität.",
        "total_dreams": "Analysierte Träume gesamt",
        "status_premium": "⭐ Status: Unbegrenztes Abo aktiv",
        "status_free": "🌿 Status: Kostenloses Konto",
        "terms_title": "📜 Allgemeine Geschäftsbedingungen",
        "terms_text": "AGB von Aureva Mind.",
        "member_space": "⚙️ Mitgliedsbereich",
        "cancel_sub": "❌ Abonnement kündigen",
        "manage_account": "📝 Registrieren",
        "pack_btn": "✨ 15 Träume-Paket (4,99 €)",
        "unlim_btn": "🚀 Unbegrenzt (12 €/Monat)"
    },
    "Italiano": {
        "welcome": "Benvenuto",
        "nav_analyze": "✨ Analizza sogno",
        "nav_journal": "📖 Diario",
        "nav_stats": "📊 Statistiche",
        "nav_terms": "📜 Termini",
        "analysis_title": "✨ Nuova Analisi Onirica",
        "dream_title": "Titolo del sogno",
        "dream_emotion": "Emozione principale",
        "dream_lucidity": "Livello di lucidità (1-5)",
        "dream_desc": "Racconta il tuo sogno in dettaglio...",
        "btn_analyze": "Analizza il mio sogno",
        "success_msg": "✨ Analisi completata con successo!",
        "interpretation_title": "Interpretazione profonda per",
        "empty_desc_warn": "Inserisci la descrizione del sogno.",
        "journal_title": "📖 Diario dei Sogni",
        "journal_desc": "Cronologia delle tue analisi.",
        "no_dreams": "Nessun sogno registrato.",
        "lucidity_label": "Livello di lucidità",
        "story_label": "Racconto",
        "stats_title": "📊 Statistiche e Stato",
        "stats_desc": "Monitora la tua attività onirica.",
        "total_dreams": "Sogni analizzati totali",
        "status_premium": "⭐ Stato: Abbonamento Illimitato Attivo",
        "status_free": "🌿 Stato: Account Gratuito",
        "terms_title": "📜 Termini e Condizioni",
        "terms_text": "Termini e condizioni di Aureva Mind.",
        "member_space": "⚙️ Area Membri",
        "cancel_sub": "❌ Annulla abbonamento",
        "manage_account": "📝 Registrati",
        "pack_btn": "✨ Pacchetto 15 Sogni (4,99 €)",
        "unlim_btn": "🚀 Illimitato (12 €/mese)"
    },
    "Português": {
        "welcome": "Bem-vindo",
        "nav_analyze": "✨ Analisar sonho",
        "nav_journal": "📖 Diário",
        "nav_stats": "📊 Estatísticas",
        "nav_terms": "📜 Termos",
        "analysis_title": "✨ Nova Análise Onírica",
        "dream_title": "Título do sonho",
        "dream_emotion": "Emoção principal",
        "dream_lucidity": "Nível de lucidez (1 a 5)",
        "dream_desc": "Descreva seu sonho em detalhes...",
        "btn_analyze": "Analisar meu sonho",
        "success_msg": "✨ Análise concluída com sucesso!",
        "interpretation_title": "Interpretação profunda para",
        "empty_desc_warn": "Insira a descrição do seu sonho.",
        "journal_title": "📖 Diário de Sonhos",
        "journal_desc": "Histórico das suas análises.",
        "no_dreams": "Nenhum sonho registrado.",
        "lucidity_label": "Nível de lucidez",
        "story_label": "Relato",
        "stats_title": "📊 Estatísticas e Status",
        "stats_desc": "Acompanhe sua atividade.",
        "total_dreams": "Total de sonhos analisados",
        "status_premium": "⭐ Status: Assinatura Ilimitada Ativa",
        "status_free": "🌿 Status: Conta Gratuita",
        "terms_title": "📜 Termos e Condições",
        "terms_text": "Termos de uso do Aureva Mind.",
        "member_space": "⚙️ Área de Membros",
        "cancel_sub": "❌ Cancelar assinatura",
        "manage_account": "📝 Cadastrar",
        "pack_btn": "✨ Pacote 15 Sonhos (€4,99)",
        "unlim_btn": "🚀 Ilimitado (€12/mês)"
    },
    "Nederlands": {
        "welcome": "Welkom",
        "nav_analyze": "✨ Droom analyseren",
        "nav_journal": "📖 Dagboek",
        "nav_stats": "📊 Statistieken",
        "nav_terms": "📜 Voorwaarden",
        "analysis_title": "✨ Nieuwe Droomanalyse",
        "dream_title": "Droomtitel",
        "dream_emotion": "Belangrijkste emotie",
        "dream_lucidity": "Luciditeit (1-5)",
        "dream_desc": "Beschrijf je droom in detail...",
        "btn_analyze": "Analyseer mijn droom",
        "success_msg": "✨ Droomanalyse succesvol voltooid!",
        "interpretation_title": "Diepe interpretatie voor",
        "empty_desc_warn": "Vul de droombeschrijving in.",
        "journal_title": "📖 Droomdagboek",
        "journal_desc": "Bekijk je droomgeschiedenis.",
        "no_dreams": "Nog geen dromen geregistreerd.",
        "lucidity_label": "Luciditeit",
        "story_label": "Verhaal",
        "stats_title": "📊 Statistieken & Status",
        "stats_desc": "Volg je droomactiviteit.",
        "total_dreams": "Totaal geanalyseerde dromen",
        "status_premium": "⭐ Status: Onbeperkt Abonnement Actief",
        "status_free": "🌿 Status: Gratis Account",
        "terms_title": "📜 Algemene Voorwaarden",
        "terms_text": "Algemene voorwaarden van Aureva Mind.",
        "member_space": "⚙️ Ledenruimte",
        "cancel_sub": "❌ Abonnement opzeggen",
        "manage_account": "📝 Registreren",
        "pack_btn": "✨ 15 Dromen Pakket (€4,99)",
        "unlim_btn": "🚀 Onbeperkt (€12/maand)"
    },
    "Polski": {
        "welcome": "Witaj",
        "nav_analyze": "✨ Analizuj sen",
        "nav_journal": "📖 Dziennik",
        "nav_stats": "📊 Statystyki",
        "nav_terms": "📜 Regulamin",
        "analysis_title": "✨ Nowa Analiza Snu",
        "dream_title": "Tytuł snu",
        "dream_emotion": "Główna emocja",
        "dream_lucidity": "Poziom świadomości (1-5)",
        "dream_desc": "Opisz swój sen...",
        "btn_analyze": "Analizuj mój sen",
        "success_msg": "✨ Analiza zakończona sukcesem!",
        "interpretation_title": "Głęboka interpretacja dla",
        "empty_desc_warn": "Wpisz opis snu.",
        "journal_title": "📖 Dziennik Snów",
        "journal_desc": "Historia Twoich analiz.",
        "no_dreams": "Brak zapisanego snu.",
        "lucidity_label": "Poziom świadomości",
        "story_label": "Opis",
        "stats_title": "📊 Statystyki i Status",
        "stats_desc": "Śledź swoją aktywność.",
        "total_dreams": "Suma przeanalizowanych snów",
        "status_premium": "⭐ Status: Subskrypcja aktywna",
        "status_free": "🌿 Status: Konto darmowe",
        "terms_title": "📜 Regulamin",
        "terms_text": "Regulamin Aureva Mind.",
        "member_space": "⚙️ Strefa Członka",
        "cancel_sub": "❌ Anuluj subskrypcję",
        "manage_account": "📝 Zarejestruj się",
        "pack_btn": "✨ Pakiet 15 Snów (4,99 €)",
        "unlim_btn": "🚀 Nieograniczony (12 €/miesiąc)"
    },
    "Русский": {
        "welcome": "Добро пожаловать",
        "nav_analyze": "✨ Анализ сна",
        "nav_journal": "📖 Дневник",
        "nav_stats": "📊 Статистика",
        "nav_terms": "📜 Условия",
        "analysis_title": "✨ Новый Анализ Сна",
        "dream_title": "Название сна",
        "dream_emotion": "Эмоция",
        "dream_lucidity": "Уровень осознанности (1-5)",
        "dream_desc": "Опишите свой сон...",
        "btn_analyze": "Анализировать мой сон",
        "success_msg": "✨ Анализ успешно выполнен!",
        "interpretation_title": "Глубокое толкование для",
        "empty_desc_warn": "Пожалуйста, введите описание сна.",
        "journal_title": "📖 Дневник снов",
        "journal_desc": "История вашых сновидений.",
        "no_dreams": "Нет записанных снов.",
        "lucidity_label": "Осознанность",
        "story_label": "Сон",
        "stats_title": "📊 Статистика и Статус",
        "stats_desc": "Отслеживайте активность.",
        "total_dreams": "Всего проанализировано снов",
        "status_premium": "⭐ Статус: Безлимит активен",
        "status_free": "🌿 Статус: Бесплатный аккаунт",
        "terms_title": "📜 Условия использования",
        "terms_text": "Условия сервиса Aureva Mind.",
        "member_space": "⚙️ Кабинет участника",
        "cancel_sub": "❌ Отменить подписку",
        "manage_account": "📝 Регистрация",
        "pack_btn": "✨ Пакет 15 снов (4,99 €)",
        "unlim_btn": "🚀 Безлимит (12 €/месяц)"
    },
    "日本語": {
        "welcome": "ようこそ",
        "nav_analyze": "✨ 夢を分析",
        "nav_journal": "📖 ジャーナル",
        "nav_stats": "📊 統計",
        "nav_terms": "📜 利用規約",
        "analysis_title": "✨ 新しい夢の分析",
        "dream_title": "夢のタイトル",
        "dream_emotion": "主な感情",
        "dream_lucidity": "明晰性レベル (1-5)",
        "dream_desc": "夢の詳細を入力してください...",
        "btn_analyze": "夢を分析する",
        "success_msg": "✨ 夢の分析が完了しました！",
        "interpretation_title": "深層心理の解釈",
        "empty_desc_warn": "夢の説明を入力してください。",
        "journal_title": "📖 夢のジャーナル",
        "journal_desc": "分析履歴の確認。",
        "no_dreams": "記録された夢はありません。",
        "lucidity_label": "明晰性レベル",
        "story_label": "内容",
        "stats_title": "📊 統計とステータス",
        "stats_desc": "活動の追跡。",
        "total_dreams": "分析された夢の総数",
        "status_premium": "⭐ ステータス: プレミアム有効",
        "status_free": "🌿 ステータス: 無料アカウント",
        "terms_title": "📜 利用規約",
        "terms_text": "Aureva Mindの利用規約です。",
        "member_space": "⚙️ 会員スペース",
        "cancel_sub": "❌ 定期購入を解約",
        "manage_account": "📝 登録",
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
        if st.button(t["manage_account"]):
            st.info("Mode inscription / connexion actif.")

# --- 5. EN-TÊTE ---
st.title(f"Aureva Mind — {t['welcome']}, {user.first_name} 🌙")

# --- 6. VRAI MENU HORIZONTAL PAR ONGLETS ---
tab_analyze, tab_journal, tab_stats, tab_terms = st.tabs([
    t["nav_analyze"], 
    t["nav_journal"], 
    t["nav_stats"], 
    t["nav_terms"]
])

# --- 7. CONTENU DE L'ONGLET : ANALYSER (ANALYSE ULTRA-POUSSÉE MOT À MOT) ---
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
            
            # Analyse ultra-détaillée basée sur l'analyse dynamique du texte saisi
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

# --- 8. CONTENU DE L'ONGLET : JOURNAL ---
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

# --- 9. CONTENU DE L'ONGLET : STATISTIQUES ---
with tab_stats:
    st.subheader(t["stats_title"])
    st.write(t["stats_desc"])
    st.markdown("---")
    st.metric(label=t["total_dreams"], value=user.dreams_count)
    if user.is_premium:
        st.success(t["status_premium"])
    else:
        st.info(t["status_free"])

# --- 10. CONTENU DE L'ONGLET : CONDITIONS GÉNÉRALES ---
with tab_terms:
    st.subheader(t["terms_title"])
    st.markdown("---")
    st.markdown(t["terms_text"])

# --- 11. BOUTONS STRIPE PERMANENTS EN BAS DE PAGE (CORRIGÉS & VISIBLES) ---
st.markdown("---")
st.markdown("### 🌙 Aureva Mind Premium")
st.write(translations[langue]["pack_btn"].split(" (")[0] + " & " + translations[langue]["unlim_btn"].split(" (")[0])
col1, col2 = st.columns(2)
with col1:
    st.link_button(translations[langue]["pack_btn"], "https://buy.stripe.com/9B68wQ9el5I21L1djxaIM00", use_container_width=True)
with col2:
    st.link_button(translations[langue]["unlim_btn"], "https://buy.stripe.com/fZu14o4Y53zUcpFenBaIM01", use_container_width=True)
