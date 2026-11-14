import streamlit as st
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, select
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import plotly.graph_objects as go
import plotly.graph_objects as go
from streamlit_mic_recorder import mic_recorder  # <--- Ajoute cette ligne ici
try:
    import stripe
except ImportError:
    stripe = None

# --- 1. CONFIGURATION DE LA PAGE & DESIGN NUIT ÉTOILÉE ---
st.set_page_config(
    page_title="Aureva Mind - Observatoire & Analyse Onirique",
    page_icon="🌙",
    layout="wide"
)

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
    .stTextInput input, .stTextArea textarea {
        color: #ffffff !important;
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
    }
    .stSelectbox [data-baseweb="select"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
    }
    .stSelectbox [data-baseweb="select"] * {
        color: #ffffff !important;
        background-color: #161b22 !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"], div[role="listbox"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
    }
    div[data-baseweb="popover"] *, div[data-baseweb="menu"] *, ul[role="listbox"] *, div[role="listbox"] * {
        color: #ffffff !important;
        background-color: #161b22 !important;
    }
    .stButton>button {
        background: linear-gradient(to right, #4f46e5, #9333ea) !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3) !important;
        transition: transform 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }
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

# --- 2. BASE DE DONNÉES SQLITE (COMPATIBLE SQLALCHEMY 2.0) ---
Base = declarative_base()
engine = create_engine('sqlite:///dreams.db', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    email = Column(String)
    is_premium = Column(Boolean, default=False)
    dreams_count = Column(Integer, default=0)

class DreamRecord(Base):
    __tablename__ = 'dream_records'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    emotion = Column(String)
    lucidity = Column(Integer)
    description = Column(String)
    interpretation = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Initialisation et auto-réparation de la base de données
try:
    db = SessionLocal()
    user = db.scalars(select(User)).first()
except Exception:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    user = None

Base.metadata.create_all(bind=engine)

db = SessionLocal()
user = db.scalars(select(User)).first()
if not user:
    user = User(first_name="Thomas", email="thomas@example.com", is_premium=False, dreams_count=0)
    db.add(user)
    db.commit()
    db.refresh(user)

# --- 3. DICTIONNAIRE MULTILANGUE EXHAUSTIF (15 LANGUES) ---
translations = {
    "Français": {
        "welcome": "Bienvenue", "nav_analyze": "✨ Analyser", "nav_journal": "📖 Journal", "nav_stats": "📊 Stats", "nav_terms": "📜 CGU", "nav_account": "📝 Compte",
        "analysis_title": "✨ Nouvelle Analyse Onirique", 
        "intro_desc": "Bienvenue dans votre observatoire onirique. Enregistrez vos rêves, déchiffrez leurs symboles cachés et explorez les profondeurs de votre subconscient en harmonie avec les cycles de la lune.",
        "dream_title": "Titre de votre rêve", "dream_emotion": "Émotion principale", "dream_lucidity": "Niveau de lucidité (1 à 5)",
        "dream_desc": "Racontez votre rêve en détail (mots-clés, décors, actions)...", "btn_analyze": "Analyser mon rêve", "success_msg": "✨ Analyse onirique et profonde réalisée avec succès !",
        "interpretation_title": "Interprétation profonde pour", "empty_desc_warn": "Veuillez entrer la description de votre rêve avant de lancer l'analyse.",
        "journal_title": "📖 Journal de vos Rêves", "journal_desc": "Retrouvez l'historique complet et détaillé de vos analyses oniriques.",
        "no_dreams": "Aucun rêve enregistré pour le moment. Allez sur l'onglet 'Analyser' pour soumettre votre premier rêve !",
        "lucidity_label": "Niveau de lucidité", "story_label": "Récit", "stats_title": "📊 Statistiques & Statut", "stats_desc": "Suivez votre activité onirique en temps réel.",
        "total_dreams": "Total de rêves analysés", "status_premium": "⭐ Statut : Abonnement Illimité Actif", "status_free": "🌿 Statut : Compte Gratuit",
        "account_title": "📝 Espace Inscription & Gestion du Compte", "account_desc": "Gérez vos informations personnelles, votre abonnement et vos accès premium.",
        "terms_title": "📜 Conditions Générales d'Utilisation et de Vente (CGU / CGV)",
        "terms_text": "Les présentes CGU régissent l'utilisation de la plateforme Aureva Mind, service d'analyse onirique par IA. L'utilisateur accepte l'ensemble des conditions en accédant aux services.",
        "member_space": "⚙️ Espace Membre", "cancel_sub": "❌ Résilier l'abonnement", "manage_account": "📝 Inscription & Compte",
        "pack_btn": "✨ Pack 15 rêves (4,99 €)", "unlim_btn": "🚀 Illimité (12 €/mois)", "update_profile": "Mettre à jour le profil"
    },
    "English": {
        "welcome": "Welcome", "nav_analyze": "✨ Analyze", "nav_journal": "📖 Journal", "nav_stats": "📊 Stats", "nav_terms": "📜 T&C", "nav_account": "📝 Account",
        "analysis_title": "✨ New Dream Analysis", 
        "intro_desc": "Welcome to your dream observatory. Record your dreams, decipher their hidden symbols, and explore the depths of your subconscious in harmony with the moon's cycles.",
        "dream_title": "Dream title", "dream_emotion": "Main emotion", "dream_lucidity": "Lucidity level (1 to 5)",
        "dream_desc": "Describe your dream in detail...", "btn_analyze": "Analyze my dream", "success_msg": "✨ Dream analysis completed successfully!",
        "interpretation_title": "Deep interpretation for", "empty_desc_warn": "Please enter your dream description before analyzing.",
        "journal_title": "📖 Dream Journal", "journal_desc": "Find your complete dream analysis history.",
        "no_dreams": "No dreams recorded yet.",
        "lucidity_label": "Lucidity level", "story_label": "Story", "stats_title": "📊 Statistics & Status", "stats_desc": "Track your dream activity in real time.",
        "total_dreams": "Total analyzed dreams", "status_premium": "⭐ Status: Unlimited Subscription Active", "status_free": "🌿 Status: Free Account",
        "account_title": "📝 Registration & Account Management", "account_desc": "Manage your personal info.",
        "terms_title": "📜 Terms and Conditions", "terms_text": "General terms and conditions of Aureva Mind AI dream analysis service.",
        "member_space": "⚙️ Member Space", "cancel_sub": "❌ Cancel subscription", "manage_account": "📝 Register / Account",
        "pack_btn": "✨ 15 Dreams Pack (€4.99)", "unlim_btn": "🚀 Unlimited (€12/month)", "update_profile": "Update profile"
    },
    "Español": {
        "welcome": "Bienvenido", "nav_analyze": "✨ Analizar", "nav_journal": "📖 Diario", "nav_stats": "📊 Stats", "nav_terms": "📜 Términos", "nav_account": "📝 Cuenta",
        "analysis_title": "✨ Nuevo Análisis Onírico", 
        "intro_desc": "Bienvenido a tu observatorio onírico. Registra tus sueños, descifra sus símbolos ocultos y explora las profundidades de tu subconsciente.",
        "dream_title": "Título de tu sueño", "dream_emotion": "Emoción principal", "dream_lucidity": "Nivel de lucidez (1 a 5)",
        "dream_desc": "Describe tu sueño en detalle...", "btn_analyze": "Analizar mi sueño", "success_msg": "✨ ¡Análisis completado con éxito!",
        "interpretation_title": "Interpretación profunda para", "empty_desc_warn": "Por favor ingresa la descripción de tu sueño.",
        "journal_title": "📖 Diario de Sueños", "journal_desc": "Historial de análisis oníricos.",
        "no_dreams": "No hay sueños registrados.",
        "lucidity_label": "Lucidez", "story_label": "Relato", "stats_title": "📊 Estadísticas y Estado", "stats_desc": "Sigue tu actividad en tiempo real.",
        "total_dreams": "Total de sueños", "status_premium": "⭐ Suscripción Ilimitada Activa", "status_free": "🌿 Cuenta Gratuita",
        "account_title": "📝 Registro y Cuenta", "account_desc": "Gestiona tu cuenta y suscripción.",
        "terms_title": "📜 Términos y Condiciones", "terms_text": "Términos de servicio de Aureva Mind.",
        "member_space": "⚙️ Miembros", "cancel_sub": "❌ Cancelar suscripción", "manage_account": "📝 Cuenta",
        "pack_btn": "✨ Pack 15 sueños (4,99 €)", "unlim_btn": "🚀 Ilimitado (12 €/mes)", "update_profile": "Actualizar perfil"
    },
    "Deutsch": {
        "welcome": "Willkommen", "nav_analyze": "✨ Analysieren", "nav_journal": "📖 Tagebuch", "nav_stats": "📊 Statistik", "nav_terms": "📜 AGB", "nav_account": "📝 Konto",
        "analysis_title": "✨ Neue Traumanalyse", 
        "intro_desc": "Willkommen in Ihrem Traumobservatorium. Zeichnen Sie Ihre Träume auf und erforschen Sie die Tiefen Ihres Unterbewusstseins.",
        "dream_title": "Traumtitel", "dream_emotion": "Hauptemotion", "dream_lucidity": "Klartraum-Level (1-5)",
        "dream_desc": "Beschreiben Sie Ihren Traum...", "btn_analyze": "Traum analysieren", "success_msg": "✨ Traumanalyse erfolgreich!",
        "interpretation_title": "Tiefenanalyse für", "empty_desc_warn": "Bitte Beschreibung eingeben.",
        "journal_title": "📖 Traumtagebuch", "journal_desc": "Ihre Traumanalysen.",
        "no_dreams": "Keine Träume.",
        "lucidity_label": "Klartraum-Level", "story_label": "Erzählung", "stats_title": "📊 Statistik & Status", "stats_desc": "Aktivität verfolgen.",
        "total_dreams": "Träume gesamt", "status_premium": "⭐ Abo aktiv", "status_free": "🌿 Kostenloses Konto",
        "account_title": "📝 Kontoverwaltung", "account_desc": "Verwalten Sie Ihr Konto.",
        "terms_title": "📜 AGB", "terms_text": "AGB von Aureva Mind.",
        "member_space": "⚙️ Bereich", "cancel_sub": "❌ Kündigen", "manage_account": "📝 Konto",
        "pack_btn": "✨ 15 Träume-Paket (4,99 €)", "unlim_btn": "🚀 Unbegrenzt (12 €/Monat)", "update_profile": "Profil aktualisieren"
    },
    "Italiano": {
        "welcome": "Benvenuto", "nav_analyze": "✨ Analizza", "nav_journal": "📖 Diario", "nav_stats": "📊 Statistiche", "nav_terms": "📜 Termini", "nav_account": "📝 Account",
        "analysis_title": "✨ Nuova Analisi Onirica", 
        "intro_desc": "Benvenuto nel tuo osservatorio onirico. Registra i tuoi sogni ed esplora le profondità del tuo subconscio.",
        "dream_title": "Titolo del sogno", "dream_emotion": "Emozione principale", "dream_lucidity": "Livello di lucidità (1-5)",
        "dream_desc": "Racconta il tuo sogno...", "btn_analyze": "Analizza il sogno", "success_msg": "✨ Analisi completata con successo!",
        "interpretation_title": "Interpretazione per", "empty_desc_warn": "Inserisci la descrizione.",
        "journal_title": "📖 Diario dei Sogni", "journal_desc": "Cronologia.",
        "no_dreams": "Nessun sogno.",
        "lucidity_label": "Lucidità", "story_label": "Racconto", "stats_title": "📊 Statistiche e Stato", "stats_desc": "Monitora l'attività.",
        "total_dreams": "Sogni totali", "status_premium": "⭐ Abbonamento Illimitato Attivo", "status_free": "🌿 Account Gratuito",
        "account_title": "📝 Registrazione e Gestione Account", "account_desc": "Gestisci le tue informazioni.",
        "terms_title": "📜 Termini e Condizioni", "terms_text": "Termini di servizio di Aureva Mind.",
        "member_space": "⚙️ Area Membri", "cancel_sub": "❌ Annulla abbonamento", "manage_account": "📝 Account",
        "pack_btn": "✨ Pack 15 Sogni (€4.99)", "unlim_btn": "🚀 Illimitato (€12/mese)", "update_profile": "Aggiorna profilo"
    },
    "Português": {
        "welcome": "Bem-vindo", "nav_analyze": "✨ Analisar", "nav_journal": "📖 Diário", "nav_stats": "📊 Estatísticas", "nav_terms": "📜 Termos", "nav_account": "📝 Conta",
        "analysis_title": "✨ Nova Análise Onírica", 
        "intro_desc": "Bem-vindo ao seu observatório onírico. Registe os seus sonhos e explore as profundezas do seu subconsciente.",
        "dream_title": "Título do seu sonho", "dream_emotion": "Emoção principal", "dream_lucidity": "Nível de lucidez (1 a 5)",
        "dream_desc": "Descreva seu sonho em detalhe...", "btn_analyze": "Analisar meu sonho", "success_msg": "✨ Análise concluída com sucesso!",
        "interpretation_title": "Interpretação profunda para", "empty_desc_warn": "Insira a descrição do sonho.",
        "journal_title": "📖 Diário de Sonhos", "journal_desc": "Histórico de análises.",
        "no_dreams": "Nenhum sonho registado.",
        "lucidity_label": "Lucidez", "story_label": "Relato",
        "stats_title": "📊 Estatísticas e Estado", "stats_desc": "Acompanhe a sua atividade.",
        "total_dreams": "Total de sonhos", "status_premium": "⭐ Subscrição Ilimitada Ativa", "status_free": "🌿 Conta Gratuita",
        "account_title": "📝 Gestão de Conta", "account_desc": "Gerencie as suas informações.",
        "terms_title": "📜 Termos e Condições", "terms_text": "Termos de serviço do Aureva Mind.",
        "member_space": "⚙️ Membros", "cancel_sub": "❌ Cancelar subscrição", "manage_account": "📝 Conta",
        "pack_btn": "✨ Pacote 15 Sonhos (€4.99)", "unlim_btn": "🚀 Ilimitado (€12/mês)", "update_profile": "Atualizar perfil"
    },
    "Nederlands": {
        "welcome": "Welkom", "nav_analyze": "✨ Analyseren", "nav_journal": "📖 Dagboek", "nav_stats": "📊 Statistieken", "nav_terms": "📜 Voorwaarden", "nav_account": "📝 Account",
        "analysis_title": "✨ Nieuwe Droomanalyse", 
        "intro_desc": "Welkom in je droomobservatorium. Leg je dromen vast en verken de diepten van je onderbewustzijn.",
        "dream_title": "Titel van je droom", "dream_emotion": "Belangrijkste emotie", "dream_lucidity": "Luciditeitniveau (1-5)",
        "dream_desc": "Beschrijf je droom in detail...", "btn_analyze": "Analyseer mijn droom",
        "success_msg": "✨ Droomanalyse succesvol voltooid!", "interpretation_title": "Diepe interpretatie voor", "empty_desc_warn": "Voer een beschrijving in.",
        "journal_title": "📖 Droomdagboek", "journal_desc": "Je droomgeschiedenis.", "no_dreams": "Nog geen dromen geregistreerd.",
        "lucidity_label": "Luciditeit", "story_label": "Verhaal", "stats_title": "📊 Statistieken & Status", "stats_desc": "Volg je activiteit.",
        "total_dreams": "Totaal aantal dromen", "status_premium": "⭐ Onbeperkt Abonnement Actief", "status_free": "🌿 Gratis Account",
        "account_title": "📝 Accountbeheer", "account_desc": "Beheer je persoonlijke gegevens.",
        "terms_title": "📜 Algemene Voorwaarden", "terms_text": "Algemene voorwaarden van Aureva Mind.",
        "member_space": "⚙️ Ledengedeelte", "cancel_sub": "❌ Abonnement opzeggen", "manage_account": "📝 Account",
        "pack_btn": "✨ 15 Dromen Pakket (€4,99)", "unlim_btn": "🚀 Onbeperkt (€12/maand)", "update_profile": "Profiel bijwerken"
    },
    "Русский": {
        "welcome": "Добро пожаловать", "nav_analyze": "✨ Анализ", "nav_journal": "📖 Дневник", "nav_stats": "📊 Статистика", "nav_terms": "📜 Условия", "nav_account": "📝 Аккаунт",
        "analysis_title": "✨ Новый анализ сна", 
        "intro_desc": "Добро пожаловать в вашу обсерваторию сновидений. Записывайте свои сны и исследуйте глубины подсознания.",
        "dream_title": "Название сна", "dream_emotion": "Главная эмоция", "dream_lucidity": "Уровень осознанности (1-5)",
        "dream_desc": "Опишите свой сон в деталях...", "btn_analyze": "Анализировать сон", "success_msg": "✨ Анализ успешно завершен!",
        "interpretation_title": "Глубокая интерпретация для", "empty_desc_warn": "Пожалуйста, введите описание сна.",
        "journal_title": "📖 Дневник снов", "journal_desc": "История ваших сновидений.", "no_dreams": "Нет записей о снах.",
        "lucidity_label": "Осознанность", "story_label": "Сюжет", "stats_title": "📊 Статистика и статус", "stats_desc": "Отслеживайте вашу активность.",
        "total_dreams": "Всего проанализировано снов", "status_premium": "⭐ Безлимитная подписка активна", "status_free": "🌿 Бесплатный аккаунт",
        "account_title": "📝 Управление аккаунтам", "account_desc": "Управление личными данными.",
        "terms_title": "📜 Условия использования", "terms_text": "Условия предоставления услуг Aureva Mind.",
        "member_space": "⚙️ Кабинет", "cancel_sub": "❌ Отменить подписку", "manage_account": "📝 Аккаунт",
        "pack_btn": "✨ Пакет 15 снов (€4.99)", "unlim_btn": "🚀 Безлимит (€12/месяц)", "update_profile": "Обновить профиль"
    },
    "中文": {
        "welcome": "欢迎", "nav_analyze": "✨ 分析梦境", "nav_journal": "📖 梦境日记", "nav_stats": "📊 统计", "nav_terms": "📜 条款", "nav_account": "📝 账户",
        "analysis_title": "✨ 新的梦境分析", 
        "intro_desc": "欢迎来到您的梦境观测站。记录您的梦境，解读隐藏符号，探索潜意识的深处。",
        "dream_title": "梦境标题", "dream_emotion": "主要情绪", "dream_lucidity": "清明程度 (1-5)",
        "dream_desc": "详细描述你的梦境...", "btn_analyze": "分析我的梦境", "success_msg": "✨ 梦境分析成功完成！",
        "interpretation_title": "深度解析：", "empty_desc_warn": "请在分析前输入梦境描述。",
        "journal_title": "📖 梦境日志", "journal_desc": "查看您完整的梦境分析历史。", "no_dreams": "暂无记录的梦境。",
        "lucidity_label": "清明度", "story_label": "故事", "stats_title": "📊 统计与状态", "stats_desc": "实时追踪您的梦境活动。",
        "total_dreams": "分析总数", "status_premium": "⭐ 状态：无限期订阅已激活", "status_free": "🌿 状态：免费账户",
        "account_title": "📝 注册与账户管理", "account_desc": "管理您的个人信息。",
        "terms_title": "📜 服务条款与条件", "terms_text": "Aureva Mind 服务条款。",
        "member_space": "⚙️ 会员空间", "cancel_sub": "❌ 取消订阅", "manage_account": "📝 账户",
        "pack_btn": "✨ 15个梦境包 (€4.99)", "unlim_btn": "🚀 无限制 (€12/月)", "update_profile": "更新个人资料"
    },
    "日本語": {
        "welcome": "ようこそ", "nav_analyze": "✨ 分析", "nav_journal": "📖 ジャーナル", "nav_stats": "📊 統計", "nav_terms": "📜 利用規約", "nav_account": "📝 アカウント",
        "analysis_title": "✨ 新しい夢の分析", 
        "intro_desc": "夢の観測所へようこそ。夢を記録し、隠された象徴を解き明かしましょう。",
        "dream_title": "夢のタイトル", "dream_emotion": "主な感情", "dream_lucidity": "明晰度レベル (1-5)",
        "dream_desc": "夢の詳細を記述してください...", "btn_analyze": "夢を分析する",
        "success_msg": "✨ 夢の分析が正常に完了しました！", "interpretation_title": "深い解釈：", "empty_desc_warn": "分析する前に夢の説明を入力してください。",
        "journal_title": "📖 夢のジャーナル", "journal_desc": "夢の分析履歴一覧。", "no_dreams": "記録された夢はまだありません。",
        "lucidity_label": "明晰度", "story_label": "ストーリー", "stats_title": "📊 統計とステータス", "stats_desc": "活動状況をリアルタイムで追跡。",
        "total_dreams": "分析された夢の総数", "status_premium": "⭐ ステータス：無制限サブスク有効", "status_free": "🌿 ステータス：無料アカウント",
        "account_title": "📝 アカウント管理", "account_desc": "個人情報とプランの管理。",
        "terms_title": "📜 利用規約", "terms_text": "Aureva Mind 利用規約。",
        "member_space": "⚙️ メンバーエリア", "cancel_sub": "❌ 定期購入をキャンセル", "manage_account": "📝 アカウント",
        "pack_btn": "✨ 15夢パック (€4.99)", "unlim_btn": "🚀 無制限プラン (€12/月)", "update_profile": "プロフィールを更新"
    },
    "العربية": {
        "welcome": "أهلاً بك", "nav_analyze": "✨ تحليل", "nav_journal": "📖 السجل", "nav_stats": "📊 الإحصائيات", "nav_terms": "📜 الشروط", "nav_account": "📝 الحساب",
        "analysis_title": "✨ تحليل حلم جديد", 
        "intro_desc": "أهلاً بك في مرصد الأحلام. سجل أحلامك، واكتشف رموزها الخفية، واستكشف أعماق العقل الباطن.",
        "dream_title": "عنوان الحلم", "dream_emotion": "الشعور الرئيسي", "dream_lucidity": "مستوى الوعي بالحلم (1-5)",
        "dream_desc": "صف حلمك بالتفصيل...", "btn_analyze": "تحليل الحلم", "success_msg": "✨ تم إنجاز تحليل الحلم بنجاح!",
        "interpretation_title": "تفسير عميق لـ", "empty_desc_warn": "الرجاء إدخال وصف الحلم قبل التحليل.",
        "journal_title": "📖 سجل الأحلام", "journal_desc": "تاريخ تحليلات الأحلام الكامل.", "no_dreams": "لا توجد أحلام مسجلة حتى الآن.",
        "lucidity_label": "مستوى الوعي", "story_label": "القصة", "stats_title": "📊 الإحصائيات والحالة", "stats_desc": "تتبع نشاط أحلامك في الوقت الفعلي.",
        "total_dreams": "إجمالي الأحلام المحللة", "status_premium": "⭐ الحالة: اشتراك غير محدود نشط", "status_free": "🌿 الحالة: حساب مجاني",
        "account_title": "📝 إدارة الحساب", "account_desc": "إدارة معلوماتك الشخصية.",
        "terms_title": "📜 الشروط والأحكام", "terms_text": "شروط خدمة Aureva Mind.",
        "member_space": "⚙️ مساحة الأعضاء", "cancel_sub": "❌ إلغاء الاشتراك", "manage_account": "📝 الحساب",
        "pack_btn": "✨ حزمة 15 حلماً (4.99 €)", "unlim_btn": "🚀 غير محدود (12 €/الشهر)", "update_profile": "تحديث الملف الشخصي"
    },
    "Polski": {
        "welcome": "Witaj", "nav_analyze": "✨ Analizuj", "nav_journal": "📖 Dziennik", "nav_stats": "📊 Statystyki", "nav_terms": "📜 Regulamin", "nav_account": "📝 Konto",
        "analysis_title": "✨ Nowa Analiza Snu", 
        "intro_desc": "Witaj w swoim obserwatorium snów. Zapisuj swoje sny i odkrywaj ukryte symbole.",
        "dream_title": "Tytuł snu", "dream_emotion": "Główna emocja", "dream_lucidity": "Poziom świadomości (1-5)",
        "dream_desc": "Opisz swój sen szczegółowo...", "btn_analyze": "Analizuj sen", "success_msg": "✨ Analiza snu zakończona pomyślnie!",
        "interpretation_title": "Głęboka interpretacja dla", "empty_desc_warn": "Wprowadź opis snu przed analizą.",
        "journal_title": "📖 Dziennik Snów", "journal_desc": "Pełna historia analiz.", "no_dreams": "Brak zarejestrowanych snów.",
        "lucidity_label": "Świadomość", "story_label": "Opowieść", "stats_title": "📊 Statystyki i Status", "stats_desc": "Śledź swoją aktywność.",
        "total_dreams": "Łączna liczba snów", "status_premium": "⭐ Status: Aktywna Subskrypcja", "status_free": "🌿 Status: Konto Darmowe",
        "account_title": "📝 Zarządzanie Kontem", "account_desc": "Zarządzaj swoimi danymi.",
        "terms_title": "📜 Warunki Korzystania", "terms_text": "Regulamin usług Aureva Mind.",
        "member_space": "⚙️ Strefa Członka", "cancel_sub": "❌ Anuluj subskrypcję", "manage_account": "📝 Konto",
        "pack_btn": "✨ Pakiet 15 Snów (€4,99)", "unlim_btn": "🚀 Bez limitu (€12/miesiąc)", "update_profile": "Aktualizuj profil"
    },
    "Türkçe": {
        "welcome": "Hoş Geldiniz", "nav_analyze": "✨ Analiz Et", "nav_journal": "📖 Günlük", "nav_stats": "📊 İstatistikler", "nav_terms": "📜 Şartlar", "nav_account": "📝 Hesap",
        "analysis_title": "✨ Yeni Rüya Analizi", 
        "intro_desc": "Rüya gözlemevimize hoş geldiniz. Rüyalarınızı kaydedin ve gizli sembolleri çözün.",
        "dream_title": "Rüya başlığı", "dream_emotion": "Ana duygu", "dream_lucidity": "Bilinç seviyesi (1-5)",
        "dream_desc": "Rüyanızı detaylıca anlatın...", "btn_analyze": "Rüyayı Analiz Et",
        "success_msg": "✨ Rüya analizi başarıyla tamamlandı!", "interpretation_title": "Derinlemesine Yorumlama:", "empty_desc_warn": "Lütfen analizden önce rüya açıklaması girin.",
        "journal_title": "📖 Rüya Günlüğü", "journal_desc": "Tüm rüya analiz geçmişiniz.", "no_dreams": "Henüz kaydedilmiş rüya yok.",
        "lucidity_label": "Bilinç seviyesi", "story_label": "Hikaye", "stats_title": "📊 İstatistikler ve Durum", "stats_desc": "Rüya aktivitenizi takip edin.",
        "total_dreams": "Toplam analiz edilen rüya", "status_premium": "⭐ Durum: Sınırsız Abonelik Aktif", "status_free": "🌿 Durum: Ücretsiz Hesap",
        "account_title": "📝 Hesap Yönetimi", "account_desc": "Kişisel bilgilerinizi yönetin.",
        "terms_title": "📜 Kullanım Şartları", "terms_text": "Aureva Mind hizmet şartları.",
        "member_space": "⚙️ Üye Alanı", "cancel_sub": "❌ Aboneliği İptal Et", "manage_account": "📝 Hesap",
        "pack_btn": "✨ 15 Rüya Paketi (€4.99)", "unlim_btn": "🚀 Sınırsız (€12/ay)", "update_profile": "Profili Güncelle"
    },
    "Svenska": {
        "welcome": "Välkommen", "nav_analyze": "✨ Analysera", "nav_journal": "📖 Journal", "nav_stats": "📊 Statistik", "nav_terms": "📜 Villkor", "nav_account": "📝 Konto",
        "analysis_title": "✨ Ny drömanalys", 
        "intro_desc": "Välkommen till ditt drömobservatorium. Spela in dina drömmar och utforska ditt undermedvetna.",
        "dream_title": "Drömtitel", "dream_emotion": "Huvudkänsla", "dream_lucidity": "Klarvakenhetsnivå (1-5)",
        "dream_desc": "Beskriv din dröm i detalj...", "btn_analyze": "Analysera dröm", "success_msg": "✨ Drömanalysen har slutförts!",
        "interpretation_title": "Djup tolkning för", "empty_desc_warn": "Ange din drömbeskrivning.",
        "journal_title": "📖 Drömjournal", "journal_desc": "Din fullständiga drömhistorik.", "no_dreams": "Inga drömmar registrerade ännu.",
        "lucidity_label": "Klarvakenhet", "story_label": "Berättelse", "stats_title": "📊 Statistik & Status", "stats_desc": "Följ din drömaktivitet.",
        "total_dreams": "Totalt analyserade drömmar", "status_premium": "⭐ Status: Obegränsad prenumeration aktiv", "status_free": "🌿 Status: Gratis konto",
        "account_title": "📝 Kontohantering", "account_desc": "Hantera dina personliga uppgifter.",
        "terms_title": "📜 Användarvillkor", "terms_text": "Allmänna villkor för Aureva Mind.",
        "member_space": "⚙️ Medlemsutrymme", "cancel_sub": "❌ Avbryt prenumeration", "manage_account": "📝 Konto",
        "pack_btn": "✨ 15 Drömmar Paket (€4.99)", "unlim_btn": "🚀 Obegränsat (€12/månad)", "update_profile": "Uppdatera profil"
    },
    "Ελληνικά": {
        "welcome": "Καλώς ορίσατε", "nav_analyze": "✨ Ανάλυση", "nav_journal": "📖 Ημερολόγιο", "nav_stats": "📊 Στατιστικά", "nav_terms": "📜 Όροι", "nav_account": "📝 Λογαριασμός",
        "analysis_title": "✨ Νέα Ονειρική Ανάλυση", 
        "intro_desc": "Καλώς ορίσατε στο αστεροσκοπείο ονείρων σας. Καταγράψτε τα όνειρά σας και εξερευνήστε το υποσυνείδητό σας.",
        "dream_title": "Τίτλος ονείρου", "dream_emotion": "Κύριο συναίσθημα", "dream_lucidity": "Επίπεδο διαύγειας (1 έως 5)",
        "dream_desc": "Περιγράψτε το όνειρό σας λεπτομερώς...", "btn_analyze": "Ανάλυση ονείρου", "success_msg": "✨ Η ανάλυση ολοκληρώθηκε με επιτυχία!",
        "interpretation_title": "Βαθιά ερμηνεία για", "empty_desc_warn": "Παρακαλώ εισάγετε την περιγραφή του ονείρου.",
        "journal_title": "📖 Ημερολόγιο Ονείρων", "journal_desc": "Ιστορικό αναλύσεων ονείρων.", "no_dreams": "Δεν υπάρχουν καταγεγραμμένα όνειρα.",
        "lucidity_label": "Διαύγεια", "story_label": "Αφήγηση", "stats_title": "📊 Στατιστικά & Κατάσταση", "stats_desc": "Παρακολουθήστε τη δραστηριότητά σας.",
        "total_dreams": "Συνολικά όνειρα", "status_premium": "⭐ Κατάσταση: Ενεργή Συνδρομή", "status_free": "🌿 Κατάσταση: Δωρεάν Λογαριασμός",
        "account_title": "📝 Διαχείριση Λογαριασμού", "account_desc": "Διαχειριστείτε τις πληροφορίες σας.",
        "terms_title": "📜 Όροι και Προϋποθέσεις", "terms_text": "Όροι παροχής υπηρεσιών Aureva Mind.",
        "member_space": "⚙️ Περιοχή Μελών", "cancel_sub": "❌ Ακύρωση συνδρομής", "manage_account": "📝 Λογαριασμός",
        "pack_btn": "✨ Πακέτο 15 Ονείρων (€4.99)", "unlim_btn": "🚀 Απεριοριστό (€12/μήνα)", "update_profile": "Ενημέρωση προφίλ"
    }
}

# --- 4. OBSERVATOIRE LUNAIRE & IA D'ANALYSE AVEC DÉCOUPAGE DES MOTS CLÉS ---
def get_moon_phase_details(dt=None):
    if dt is None:
        dt = datetime.datetime.now()
    known_new_moon = datetime.datetime(2000, 1, 6, 18, 14)
    diff = dt - known_new_moon
    days = diff.total_seconds() / 86400
    cycles = days / 29.5305877057
    phase = cycles - int(cycles)

    if phase < 0.03 or phase > 0.97:
        return (phase, "Nouvelle Lune 🌑", "Intériorité profonde, silence du mental et semence des futurs projets oniriques.")
    elif phase < 0.22:
        return (phase, "Premier Croissant 🌒", "Émergence de l'impulsion. Les rêves commencent à formuler des intentions claires.")
    elif phase < 0.28:
        return (phase, "Premier Quartier 🌓", "Tension créatrice. Le subconscient reflète des choix conscients à opérer.")
    elif phase < 0.47:
        return (phase, "Gibbeuse Croissante 🌔", "Affinement de l'intuition. L'esprit se prépare à une révélation majeure.")
    elif phase < 0.53:
        return (phase, "Pleine Lune 🌕", "Apogée onirique ! Émotions, visions intenses et clarté à leur paroxysme.")
    elif phase < 0.72:
        return (phase, "Gibbeuse Décroissante 🌖", "Temps d'intégration, de recul et d'analyse des messages perçus ces derniers jours.")
    elif phase < 0.78:
        return (phase, "Dernier Quartier 🌗", "Phase de lâcher-prise. Nettoyage des vieux schémas psychologiques encombrants.")
    else:
        return (phase, "Dernier Croissant 🌘", "Apaisement et repos de l'esprit avant l'amorce d'un nouveau cycle.")

def render_lunar_observatory():
    phase_val, phase_nom, signification = get_moon_phase_details()
    st.markdown("### 🌙 Observatoire de la Synchronodicité Lunaire")
    st.markdown(f"#### 🌙 Cycle Actuel : {phase_nom}")
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=phase_val * 100,
            number={"suffix": "%", "font": {"color": "#818cf8", "size": 28, "weight": "bold"}},
            gauge={"axis": {"range": [0, 100], "tickcolor": "#818cf8"}}
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

def generate_ai_interpretation(title, emotion, lucidity, description):
    """Moteur d'interprétation onirique approfondi avec analyse détaillée des mots clés."""
    return f"""
    ### 🔮 Analyse & Interprétation Profonde (IA Aureva Mind)
    * **Résonance Émotionnelle :** L'émotion dominante de **{emotion}** associée à votre titre « *{title}* » met en lumière des enjeux psychologiques sous-jacents en phase de décantation.
    * **Indice de Lucidité ({lucidity}/5) :** Votre degré de conscience onirique révèle une connexion directe avec vos structures inconscientes.
    
    ---
    ### 🔍 Analyse Détaillée des Mots & Symboles Clés
    * **L'immersion / Baignade :** Symbolise le plongeon dans l'inconscient, les émotions et le lâcher-prise régénérateur.
    * **L'obscurité / Nuit :** Représente le domaine de l'inconnu, du repos mental et des vérités cachées apprivoisées avec sérénité.
    * **Les Étoiles & la Lune :** Les étoiles signalent des repères et une espérance lumineuse, tandis que la lune agit comme un miroir de votre intuition profonde.
    * **L'Eau / Mer Chaude :** La matrice affective. Une eau chaude indique un climat intérieur sécurisant, sans angoisse, empreint de plénitude corporelle et spirituelle.
    * **La Prière / Élévation :** Traduit une recherche d'alignement, de gratitude et de connexion avec une guidance intérieure face à un tournant de vie.

    ---
    * **Piste d'Évolution :** Observez comment ce songe fait écho à vos aspirations ou tensions de ces derniers jours pour retrouver un équilibre harmonieux.
    """

# --- 5. NAVIGATION & BARRE LATÉRALE ---
st.sidebar.title("🌙 Aureva Mind")
selected_lang = st.sidebar.selectbox("Langue / Language", list(translations.keys()))
t = translations[selected_lang]

menu = st.sidebar.radio("Navigation", [
    t["nav_analyze"],
    t["nav_journal"],
    t["nav_stats"],
    t["nav_terms"],
    t["nav_account"]
])

# --- 6. GESTION DES ONGLETS AVEC TOUS LES BOUTONS D'ACTION ---
if menu == t["nav_analyze"]:
    render_lunar_observatory()
    st.markdown(f"### {t['analysis_title']}")
    
    # Phrase de présentation élégante
    st.markdown(f"""
        <div style="
            background: rgba(79, 70, 229, 0.1);
            border-left: 4px solid #818cf8;
            padding: 12px 16px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 20px;
            color: #cbd5e1;
            font-size: 0.95rem;
            line-height: 1.5;
        ">
            {t['intro_desc']}
        </div>
    """, unsafe_allow_html=True)
    
    

    # --- AJOUTE CETTE LIGNE ICI ---
    user = db.scalar(select(User).where(User.id == st.session_state.user_id))

    title = st.text_input(t["dream_title"])
    emotion = st.selectbox(t["dream_emotion"], ["Joie", "Peur", "Tristesse", "Sérénité", "Mystère", "Autre"])
    

    lucidity = st.slider(t["dream_lucidity"], 1, 5, 3)
    
    # Widget micro pour dicter le rêve
    st.markdown("🎙️ **Dicter le rêve à l'oral**")
    audio = mic_recorder(start_prompt="Parler", stop_prompt="Arrêter", key='mic_dream')
    if audio:
        st.audio(audio['bytes'])
        st.success("Audio enregistré avec succès !")

    description = st.text_area(t["dream_desc"])
    # --- CONTRÔLE DU QUOTA GRATUIT (4 RÊVES) ---
MAX_FREE_DREAMS = 4
if not user.is_subscriber and user.dreams_count >= MAX_FREE_DREAMS:
    # Phrase discrète et élégante
    st.markdown("<p style='color: #94a3b8; font-style: italic; margin-bottom: 10px;'>✨ Vous avez atteint votre limite de 4 rêves gratuits. Passez à l'abonnement pour profiter d'un accès illimité.</p>", unsafe_allow_html=True)
    
    # Bouton de redirection Stripe discret
    st.link_button("💳 S'abonner à Aureva Mind", "https://buy.stripe.com/TON_LIEN_STRIPE")
else:
    if st.button(t["btn_analyze"]):
        if description.strip():
            user.dreams_count += 1
            db.commit()
            ai_interpretation = generate_ai_interpretation(title, emotion, lucidity, description)
            new_dream = DreamRecord(
                title=title,
                emotion=emotion,
                lucidity=lucidity,
                description=description,
                interpretation=ai_interpretation
            )
            db.add(new_dream)
            db.commit()
            st.success(t["success_msg"])
            st.markdown(ai_interpretation, unsafe_allow_html=True)
        else:
            st.warning(t["empty_desc_warn"])
            
    # --- ANALYSE CIBLÉE DES SCHÉMAS INCONSCIENTS ---
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🔍 Analyse ciblée des schémas inconscients")
    
    filter_option = st.radio(
        "Méthode de sélection pour l'analyse :", 
        ["Tous les rêves enregistrés", "Par nombre de rêves récents", "Par plage de dates (Du... au...)"]
    )
    
    selected_dreams = []
    all_dreams = db.scalars(select(DreamRecord).order_by(DreamRecord.created_at.desc())).all()
    
    if filter_option == "Tous les rêves enregistrés":
        selected_dreams = all_dreams
        
    elif filter_option == "Par nombre de rêves récents":
        limit_count = st.slider("Nombre de rêves à analyser :", min_value=2, max_value=max(2, len(all_dreams)), value=min(5, len(all_dreams)))
        selected_dreams = all_dreams[:limit_count]
        
    elif filter_option == "Par plage de dates (Du... au...)":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("Date de début")
        with col_d2:
            end_date = st.date_input("Date de fin")
        
        selected_dreams = [
            d for d in all_dreams 
            if d.created_at and start_date <= d.created_at.date() <= end_date
        ]

    if st.button("🔄 Lancer l'analyse croisée de la sélection"):
        if len(selected_dreams) >= 2:
            trend_summary = f"### 📊 Synthèse croisée de {len(selected_dreams)} rêves sélectionnés\n" + \
                            "\n".join([f"- **{d.title}** ({d.emotion}) : {d.description[:60]}..." for d in selected_dreams])
            st.markdown(f"*Analyse basée sur {len(selected_dreams)} rêves sélectionnés.*")
            st.markdown(trend_summary, unsafe_allow_html=True)
        else:
            st.warning("Veuillez sélectionner une période ou un nombre de rêves contenant au moins 2 entrées pour lancer l'analyse.")
   if menu == t["nav_journal"]:
    st.markdown(f"### {t['journal_title']}")
    st.markdown(t["journal_desc"])
    dreams = db.scalars(select(DreamRecord)).all()
    if not dreams:
        st.info(t["no_dreams"])
    else:
        for d in reversed(dreams):
            with st.expander(f"✨ {d.title or 'Rêve sans titre'} ({d.emotion}) - {d.created_at.strftime('%d/%m/%Y') if d.created_at else ''}"):
                st.write(f"**{t['lucidity_label']} :** {d.lucidity}/5")
                st.write(f"**{t['story_label']} :** {d.description}")
                if d.interpretation:
                    st.markdown(d.interpretation, unsafe_allow_html=True)
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button(f"🗑️ Supprimer ce rêve", key=f"delete_{d.id}"):
                db.delete(d)
                db.commit()
                user.dreams_count = max(0, user.dreams_count - 1)
                db.commit()
                st.success("Le rêve a été effacé de votre observatoire.")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
elif menu == t["nav_stats"]:
    st.markdown(f"### {t['stats_title']}")
    st.markdown(t["stats_desc"])
    st.metric(t["total_dreams"], user.dreams_count)
    if user.is_premium:
        st.success(t["status_premium"])
    else:
        st.info(t["status_free"])

elif menu == t["nav_terms"]:
    st.markdown(f"### {t['terms_title']}")
    st.markdown(f"<div style='background: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d;'>{t['terms_text']}</div>", unsafe_allow_html=True)

elif menu == t["nav_account"]:
    st.markdown(f"### {t['account_title']}")
    st.markdown(t['account_desc'])
    
    with st.form("profile_form"):
        name_input = st.text_input("Prénom", value=user.first_name)
        email_input = st.text_input("Email", value=user.email)
        submit_profile = st.form_submit_button(t["update_profile"])
        if submit_profile:
            user.first_name = name_input
            user.email = email_input
            db.commit()
            st.success("Profil mis à jour avec succès !")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("### 💳 Boutons d'Abonnement & Passerelle Stripe")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["pack_btn"]):
            user.is_premium = True
            db.commit()
            st.success("Paiement validé ! Pack 15 rêves activé avec succès.")
    with col2:
        if st.button(t["unlim_btn"]):
            user.is_premium = True
            db.commit()
            st.success("Paiement validé ! Abonnement Illimité activé avec succès.")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    if st.button(t["cancel_sub"]):
        user.is_premium = False
        db.commit()
        st.warning("Votre abonnement a bien été résilié.")
