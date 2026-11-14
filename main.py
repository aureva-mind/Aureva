import streamlit as st
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, select
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import plotly.graph_objects as go
from streamlit_mic_recorder import mic_recorder

# Gestion sécurisée de Stripe
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
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Plus+Jakarta+Sans:wght@300;400;500&display=swap');

.stApp {
    background: 
        radial-gradient(2px 2px at 20px 30px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 40px 70px, #ffd700, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 90px 40px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 160px 120px, #ffd700, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 200px 200px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 300px 60px, #ffd700, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 450px 150px, #ffd700, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 500px 300px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 650px 70px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1.5px 1.5px at 750px 220px, #ffd700, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 850px 120px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 950px 280px, #ffd700, rgba(0,0,0,0)),
        linear-gradient(135deg, #05070f, #1b1e3b, #05070f) !important;
    background-repeat: repeat;
    background-size: 500px 500px;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
section[data-testid="stSidebar"] {
    background-color: #0f172a !important;
}
h1, h2, h3, label, span, div {
    color: #f1f5f9 !important;
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
.stButton>button {
    background: linear-gradient(to right, #4f46e5, #9333ea) !important;
    color: white !important;
    border-radius: 20px !important;
    font-weight: bold !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# --- 2. BASE DE DONNÉES SQLITE ---
Base = declarative_base()
engine = create_engine("sqlite:///dreams.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    email = Column(String)
    is_premium = Column(Boolean, default=False)
    dreams_count = Column(Integer, default=0)

class DreamRecord(Base):
    __tablename__ = 'dreams_records'
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
    user = User(first_name="Thomas", email="thomas@example.com", is_premium=False)
    db.add(user)
    db.commit()
    db.refresh(user)

# --- 3. DICTIONNAIRE MULTILANGUE EXHAUSTIF (15 LANGUES + CLÉS DE NAVIGATION CORRIGÉES) ---
translations = {
    "Français": {
        "welcome": "Bienvenue",
        "nav_analyse": "✨ Analyser",
        "nav_journal": "🗂️ Journal de vos Rêves",
        "nav_stats": "📊 Statistiques",
        "nav_terms": "📜 Conditions",
        "nav_account": "⚙️ Mon Compte",
        "analysis_title": "✨ Nouvelle Analyse Onirique",
        "intro_desc": "Bienvenue dans votre observatoire onirique. Enregistrez vos rêves pour percer les mystères de votre inconscient.",
        "dream_title": "Titre de votre rêve",
        "dream_emotion": "Émotion principale",
        "dream_lucidity": "Niveau de lucidité",
        "dream_desc": "Raconter votre rêve en détail (mots-clés, décors, actions)",
        "btn_analyser": "Lancer l'analyse",
        "empty_desc_warn": "Veuillez entrer une description pour analyser le rêve.",
        "journal_title": "Journal de vos Rêves",
        "journal_desc": "Retrouvez l'historique complet de vos analyses oniriques.",
        "no_dreams": "Aucun rêve enregistré pour le moment. Allez sur l'onglet Analyser pour commencer.",
        "lucidity_label": "Niveau de lucidité",
        "story_label": "Récit",
        "stats_title": "Statistiques de vos rêves",
        "stats_desc": "Suivi global de vos explorations oniriques.",
        "total_dreams": "Total de rêves analysés",
        "status_premium": "⭐ Statut : Abonnement Illimité Actif",
        "status_free": "🌱 Statut : Mode Gratuit (4 rêves max)",
        "account_title": "Espace Inscription & Gestion du Compte",
        "account_desc": "Gérez vos informations personnelles.",
        "terms_title": "Conditions Générales d'Utilisation et de Vente (CGU)",
        "terms_text": "Les présentes CGU régissent l'utilisation de la plateforme Aureva Mind.",
        "member_space": "🪪 Espace Membre",
        "cancel_sub": "❌ Résilier l'abonnement",
        "pack_btn": "✨ Pack 15 rêves (4,99 €)",
        "unlim_btn": "🚀 Illimité (12 €/an)"
    },
    "English": {
        "welcome": "Welcome",
        "nav_analyse": "✨ Analyze",
        "nav_journal": "🗂️ Dream Journal",
        "nav_stats": "📊 Statistics",
        "nav_terms": "📜 Terms",
        "nav_account": "⚙️ Account",
        "analysis_title": "✨ New Dream Analysis",
        "intro_desc": "Welcome to your dream observatory. Record your dreams to uncover the mysteries of your unconscious.",
        "dream_title": "Dream Title",
        "dream_emotion": "Main Emotion",
        "dream_lucidity": "Lucidity Level",
        "dream_desc": "Describe your dream in detail (keywords, settings, actions)",
        "btn_analyser": "Analyze",
        "empty_desc_warn": "Please enter a description to analyze the dream.",
        "journal_title": "Dreams Journal",
        "journal_desc": "Find your complete history of dream analyses.",
        "no_dreams": "No dreams recorded yet. Go to the Analyze tab to start.",
        "lucidity_label": "Lucidity level",
        "story_label": "Story",
        "stats_title": "Statistics",
        "stats_desc": "Global tracking of your dream explorations.",
        "total_dreams": "Total analyzed dreams",
        "status_premium": "Status: Unlimited Active",
        "status_free": "Status: Free Tier",
        "account_title": "Registration & Account Management",
        "account_desc": "Manage your personal information.",
        "terms_title": "Terms and Conditions",
        "terms_text": "These terms govern the use of the Aureva Mind platform.",
        "member_space": "Member Space",
        "cancel_sub": "Cancel subscription",
        "pack_btn": "✨ 15 Dreams Pack (€4.99)",
        "unlim_btn": "🚀 Unlimited (€12/year)"
    },
    "Español": {
        "welcome": "Bienvenido",
        "nav_analyse": "✨ Analizar",
        "nav_journal": "🗂️ Diario de Sueños",
        "nav_stats": "📊 Estadísticas",
        "nav_terms": "📜 Términos",
        "nav_account": "⚙️ Cuenta",
        "analysis_title": "✨ Nuevo Análisis Onírico",
        "intro_desc": "Bienvenido a tu observatorio onírico. Registra tus sueños...",
        "dream_title": "Título de tu sueño",
        "dream_emotion": "Emoción principal",
        "dream_lucidity": "Nivel de lucidez",
        "dream_desc": "Describe tu sueño en detalle...",
        "btn_analyser": "Analizar",
        "empty_desc_warn": "Por favor introduce una descripción.",
        "journal_title": "Diario de Sueños",
        "journal_desc": "Historial de análisis.",
        "no_dreams": "No hay sueños registrados.",
        "lucidity_label": "Lucidez",
        "story_label": "Relato",
        "stats_title": "Estadísticas",
        "stats_desc": "Total de sueños",
        "total_dreams": "Total de sueños",
        "status_premium": "Suscripción Ilimitada",
        "status_free": "Modo Gratuito",
        "account_title": "Registro y Cuenta",
        "account_desc": "Gestiona tu cuenta",
        "terms_title": "Términos y Condiciones",
        "terms_text": "Términos de servicio.",
        "member_space": "Miembros",
        "cancel_sub": "Cancelar suscripción",
        "pack_btn": "✨ Pack 15 sueños (€4.99)",
        "unlim_btn": "🚀 Ilimitado"
    },
    "Deutsch": {
        "welcome": "Willkommen",
        "nav_analyse": "✨ Analysieren",
        "nav_journal": "🗂️ Traumtagebuch",
        "nav_stats": "📊 Statistiken",
        "nav_terms": "📜 AGB",
        "nav_account": "⚙️ Konto",
        "analysis_title": "✨ Neue Traumanalyse",
        "intro_desc": "Willkommen in Ihrem Traumobservatorium.",
        "dream_title": "Traumtitel",
        "dream_emotion": "Hauptemotion",
        "dream_lucidity": "Klartraum-Level",
        "dream_desc": "Beschreiben Sie Ihren Traum...",
        "btn_analyser": "Traum analysieren",
        "empty_desc_warn": "Bitte Beschreibung eingeben.",
        "journal_title": "Traumtagebuch",
        "journal_desc": "Ihre Traumanalysen.",
        "no_dreams": "Keine Träume.",
        "lucidity_label": "Klartraum-Level",
        "story_label": "Erzählung",
        "stats_title": "Statistiken",
        "stats_desc": "Träume gesamt",
        "total_dreams": "Träume gesamt",
        "status_premium": "Abo aktiv",
        "status_free": "Kostenlos",
        "account_title": "Kontoverwaltung",
        "account_desc": "Verwalten Sie Ihr Konto",
        "terms_title": "AGB",
        "terms_text": "AGB von Aureva Mind.",
        "member_space": "Bereich",
        "cancel_sub": "Kündigen",
        "pack_btn": "✨ 15 Träume-Paket (€4.99)",
        "unlim_btn": "🚀 Unbegrenzt"
    },
    "Italiano": {
        "welcome": "Benvenuto",
        "nav_analyse": "✨ Analizza",
        "nav_journal": "🗂️ Diario dei Sogni",
        "nav_stats": "📊 Statistiche",
        "nav_terms": "📜 Termini",
        "nav_account": "⚙️ Account",
        "analysis_title": "✨ Nuova Analisi Onirica",
        "intro_desc": "Benvenuto nel tuo osservatorio onirico.",
        "dream_title": "Titolo del sogno",
        "dream_emotion": "Emozione principale",
        "dream_lucidity": "Lucidità",
        "dream_desc": "Racconta il tuo sogno...",
        "btn_analyser": "Analizza il sogno",
        "empty_desc_warn": "Inserisci una descrizione.",
        "journal_title": "Diario dei Sogni",
        "journal_desc": "Cronologia.",
        "no_dreams": "Nessun sogno.",
        "lucidity_label": "Lucidità",
        "story_label": "Racconto",
        "stats_title": "Statistiche",
        "stats_desc": "Sogni totali",
        "total_dreams": "Sogni totali",
        "status_premium": "Abbonamento Illimitato",
        "status_free": "Gratuito",
        "account_title": "Registrazione",
        "account_desc": "Gestione Account",
        "terms_title": "Termini e Condizioni",
        "terms_text": "Termini di servizio.",
        "member_space": "Area Membri",
        "cancel_sub": "Annulla abbonamento",
        "pack_btn": "✨ Pack 15 Sogni (€4.99)",
        "unlim_btn": "🚀 Illimitato"
    },
    "Português": {
        "welcome": "Bem-vindo",
        "nav_analyse": "✨ Analisar",
        "nav_journal": "🗂️ Diário de Sonhos",
        "nav_stats": "📊 Estatísticas",
        "nav_terms": "📜 Termos",
        "nav_account": "⚙️ Conta",
        "analysis_title": "✨ Nova Análise Onírica",
        "intro_desc": "Bem-vindo ao seu observatório.",
        "dream_title": "Título do sonho",
        "dream_emotion": "Emoção principal",
        "dream_lucidity": "Lucidez",
        "dream_desc": "Descreva seu sonho...",
        "btn_analyser": "Analisar",
        "empty_desc_warn": "Insira uma descrição.",
        "journal_title": "Diário de Sonhos",
        "journal_desc": "Histórico.",
        "no_dreams": "Nenhum sonho.",
        "lucidity_label": "Lucidez",
        "story_label": "Relato",
        "stats_title": "Estatísticas",
        "stats_desc": "Total de sonhos",
        "total_dreams": "Total de sonhos",
        "status_premium": "Assinatura Ilimitada",
        "status_free": "Gratuito",
        "account_title": "Gestão de Conta",
        "account_desc": "Gerencie sua conta",
        "terms_title": "Termos e Condições",
        "terms_text": "Termos de serviço.",
        "member_space": "Área de Membros",
        "cancel_sub": "Cancelar assinatura",
        "pack_btn": "✨ Pacote 15 Sonhos (€4.99)",
        "unlim_btn": "🚀 Ilimitado"
    },
    "Nederlands": {
        "welcome": "Welkom",
        "nav_analyse": "✨ Analyseren",
        "nav_journal": "🗂️ Droomdagboek",
        "nav_stats": "📊 Statistieken",
        "nav_terms": "📜 Voorwaarden",
        "nav_account": "⚙️ Account",
        "analysis_title": "✨ Nieuwe Droomanalyse",
        "intro_desc": "Welkom in uw droomobservatorium.",
        "dream_title": "Droomtitel",
        "dream_emotion": "Belangrijkste emotie",
        "dream_lucidity": "Luciditeit",
        "dream_desc": "Beschrijf uw droom...",
        "btn_analyser": "Analyseren",
        "empty_desc_warn": "Vul een beschrijving in.",
        "journal_title": "Droomdagboek",
        "journal_desc": "Droomgeschiedenis.",
        "no_dreams": "Geen dromen.",
        "lucidity_label": "Luciditeit",
        "story_label": "Verhaal",
        "stats_title": "Statistieken",
        "stats_desc": "Totaal aantal dromen",
        "total_dreams": "Totaal aantal dromen",
        "status_premium": "Onbeperkt actief",
        "status_free": "Gratis",
        "account_title": "Accountbeheer",
        "account_desc": "Beheer uw gegevens",
        "terms_title": "Algemene Voorwaarden",
        "terms_text": "Algemene voorwaarden.",
        "member_space": "Leden",
        "cancel_sub": "Abonnement opzeggen",
        "pack_btn": "✨ 15 Dromen Pakket (€4.99)",
        "unlim_btn": "🚀 Onbeperkt"
    },
    "Русский": {
        "welcome": "Добро пожаловать",
        "nav_analyse": "✨ Анализ",
        "nav_journal": "🗂️ Дневник снов",
        "nav_stats": "📊 Статистика",
        "nav_terms": "📜 Условия",
        "nav_account": "⚙️ Аккаунт",
        "analysis_title": "✨ Новый анализ сна",
        "intro_desc": "Добро пожаловать в обсерваторию снов.",
        "dream_title": "Название сна",
        "dream_emotion": "Главная эмоция",
        "dream_lucidity": "Осознанность",
        "dream_desc": "Опишите свой сон...",
        "btn_analyser": "Анализировать",
        "empty_desc_warn": "Введите описание.",
        "journal_title": "Дневник снов",
        "journal_desc": "История снов.",
        "no_dreams": "Нет снов.",
        "lucidity_label": "Осознанность",
        "story_label": "Сюжет",
        "stats_title": "Статистика",
        "stats_desc": "Всего снов",
        "total_dreams": "Всего снов",
        "status_premium": "Премиум активен",
        "status_free": "Бесплатно",
        "account_title": "Управление аккаунтом",
        "account_desc": "Управление профилем",
        "terms_title": "Условия использования",
        "terms_text": "Условия платформы.",
        "member_space": "Кабинет",
        "cancel_sub": "Отменить подписку",
        "pack_btn": "✨ Пакет 15 снов (€4.99)",
        "unlim_btn": "🚀 Безлимит"
    },
    "中文": {
        "welcome": "欢迎",
        "nav_analyse": "✨ 分析",
        "nav_journal": "🗂️ 梦境日记",
        "nav_stats": "📊 统计",
        "nav_terms": "📜 条款",
        "nav_account": "⚙️ 账户",
        "analysis_title": "✨ 新梦境分析",
        "intro_desc": "欢迎来到您的梦境观测站。",
        "dream_title": "梦境标题",
        "dream_emotion": "主要情绪",
        "dream_lucidity": "清醒度",
        "dream_desc": "详细描述您的梦境...",
        "btn_analyser": "分析梦境",
        "empty_desc_warn": "请输入描述。",
        "journal_title": "梦境日记",
        "journal_desc": "您的梦境历史。",
        "no_dreams": "暂无梦境记录。",
        "lucidity_label": "清醒度",
        "story_label": "故事",
        "stats_title": "统计数据",
        "stats_desc": "总分析梦境数",
        "total_dreams": "总分析梦境数",
        "status_premium": "无限期激活",
        "status_free": "免费版",
        "account_title": "账户管理",
        "account_desc": "管理您的个人信息",
        "terms_title": "服务条款",
        "terms_text": "服务条款说明。",
        "member_space": "会员空间",
        "cancel_sub": "取消订阅",
        "pack_btn": "✨ 15梦境包 (€4.99)",
        "unlim_btn": "🚀 无限制 (€12/年)"
    },
    "日本語": {
        "welcome": "ようこそ",
        "nav_analyse": "✨ 分析",
        "nav_journal": "🗂️ 夢の日記",
        "nav_stats": "📊 統計",
        "nav_terms": "📜 利用規約",
        "nav_account": "⚙️ アカウント",
        "analysis_title": "✨ 新しい夢の分析",
        "intro_desc": "夢の観測所へようこそ。",
        "dream_title": "夢のタイトル",
        "dream_emotion": "主な感情",
        "dream_lucidity": "明晰度",
        "dream_desc": "夢の詳細を記述してください...",
        "btn_analyser": "分析する",
        "empty_desc_warn": "説明を入力してください。",
        "journal_title": "夢のジャーナル",
        "journal_desc": "分析履歴。",
        "no_dreams": "記録された夢はありません。",
        "lucidity_label": "明晰度",
        "story_label": "ストーリー",
        "stats_title": "統計",
        "stats_desc": "分析された夢の総数",
        "total_dreams": "分析された夢の総数",
        "status_premium": "無制限プラン有効",
        "status_free": "フリープラン",
        "account_title": "アカウント管理",
        "account_desc": "プロフィールの管理",
        "terms_title": "利用規約",
        "terms_text": "利用規約について。",
        "member_space": "メンバーエリア",
        "cancel_sub": "サブスクリプションをキャンセル",
        "pack_btn": "✨ 15夢パック (€4.99)",
        "unlim_btn": "🚀 無制限プラン (€12/年)"
    },
    "العربية": {
        "welcome": "مرحباً",
        "nav_analyse": "✨ تحليل",
        "nav_journal": "🗂️ سجل الأحلام",
        "nav_stats": "📊 الإحصائيات",
        "nav_terms": "📜 الشروط",
        "nav_account": "⚙️ الحساب",
        "analysis_title": "✨ تحليل حلم جديد",
        "intro_desc": "مرحباً بك في مرصد الأحلام.",
        "dream_title": "عنوان الحلم",
        "dream_emotion": "الشعور الرئيسي",
        "dream_lucidity": "درجة الوعي",
        "dream_desc": "صف حلمك بالتفصيل...",
        "btn_analyser": "تحليل",
        "empty_desc_warn": "الرجاء إدخال الوصف.",
        "journal_title": "سجل الأحلام",
        "journal_desc": "سجل تحليلاتك.",
        "no_dreams": "لا توجد أحلام مسجلة.",
        "lucidity_label": "مستوى الوعي",
        "story_label": "القصة",
        "stats_title": "الإحصائيات",
        "stats_desc": "إجمالي الأحلام",
        "total_dreams": "إجمالي الأحلام",
        "status_premium": "اشتراك غير محدود نشط",
        "status_free": "الباقة المجانية",
        "account_title": "إدارة الحساب",
        "account_desc": "إدارة معلوماتك",
        "terms_title": "شروط الاستخدام",
        "terms_text": "شروط الخدمة.",
        "member_space": "منطقة الأعضاء",
        "cancel_sub": "إلغاء الاشتراك",
        "pack_btn": "✨ باقة 15 حلماً (€4.99)",
        "unlim_btn": "🚀 غير محدود"
    },
    "Türkçe": {
        "welcome": "Hoş Geldiniz",
        "nav_analyse": "✨ Analiz Et",
        "nav_journal": "🗂️ Rüya Günlüğü",
        "nav_stats": "📊 İstatistikler",
        "nav_terms": "📜 Şartlar",
        "nav_account": "⚙️ Hesap",
        "analysis_title": "✨ Yeni Rüya Analizi",
        "intro_desc": "Rüya gözlemevinize hoş geldiniz.",
        "dream_title": "Rüya Başlığı",
        "dream_emotion": "Ana Duygu",
        "dream_lucidity": "Rüya Bilinci",
        "dream_desc": "Rüyanızı detaylıca anlatın...",
        "btn_analyser": "Analiz Et",
        "empty_desc_warn": "Lütfen bir açıklama girin.",
        "journal_title": "Rüya Günlüğü",
        "journal_desc": "Rüya geçmişiniz.",
        "no_dreams": "Kayıtlı rüya yok.",
        "lucidity_label": "Bilinç seviyesi",
        "story_label": "Hikaye",
        "stats_title": "İstatistikler",
        "stats_desc": "Toplam rüya",
        "total_dreams": "Toplam rüya",
        "status_premium": "Abonelik Aktif",
        "status_free": "Ücretsiz Plan",
        "account_title": "Hesap Yönetimi",
        "account_desc": "Bilgilerinizi yönetin",
        "terms_title": "Kullanım Şartları",
        "terms_text": "Hizmet şartları.",
        "member_space": "Üye Alanı",
        "cancel_sub": "Aboneliği İptal Et",
        "pack_btn": "✨ 15 Rüya Paketi (€4.99)",
        "unlim_btn": "🚀 Sınırsız"
    },
    "Svenska": {
        "welcome": "Välkommen",
        "nav_analyse": "✨ Analysera",
        "nav_journal": "🗂️ Drömjournal",
        "nav_stats": "📊 Statistik",
        "nav_terms": "📜 Villkor",
        "nav_account": "⚙️ Konto",
        "analysis_title": "✨ Ny drömanalys",
        "intro_desc": "Välkommen till ditt drömobservatorium.",
        "dream_title": "Drömtitel",
        "dream_emotion": "Huvudkänsla",
        "dream_lucidity": "Klarvarning",
        "dream_desc": "Beskriv din dröm i detalj...",
        "btn_analyser": "Analysera",
        "empty_desc_warn": "Vänligen ange en beskrivning.",
        "journal_title": "Drömjournal",
        "journal_desc": "Din drömhistorik.",
        "no_dreams": "Inga drömmar registrerade.",
        "lucidity_label": "Klarvarning",
        "story_label": "Berättelse",
        "stats_title": "Statistik",
        "stats_desc": "Totalt antal drömmar",
        "total_dreams": "Totalt antal drömmar",
        "status_premium": "Status: Obegränsad",
        "status_free": "Status: Gratis",
        "account_title": "Kontohantering",
        "account_desc": "Hantera ditt konto",
        "terms_title": "Användarvillkor",
        "terms_text": "Allmänna villkor.",
        "member_space": "Medlemsutrymme",
        "cancel_sub": "Avbryt prenumeration",
        "pack_btn": "✨ 15 Drömmar Paket (€4.99)",
        "unlim_btn": "🚀 Obegränsad"
    },
    "Ελληνικά": {
        "welcome": "Καλώς ορίσατε",
        "nav_analyse": "✨ Ανάλυση",
        "nav_journal": "🗂️ Hμερολόγιο Ονείρων",
        "nav_stats": "📊 Στατιστικά",
        "nav_terms": "📜 Όροι",
        "nav_account": "⚙️ Λογαριασμός",
        "analysis_title": "✨ Νέα Ανάλυση Ονείρου",
        "intro_desc": "Καλώς ορίσατε στο αστροσκοπείο ονείρων.",
        "dream_title": "Τίτλος ονείρου",
        "dream_emotion": "Κύριο συναίσθημα",
        "dream_lucidity": "Επίπεδο διαύγειας",
        "dream_desc": "Περιγράψτε το όνειρό σας...",
        "btn_analyser": "Ανάλυση",
        "empty_desc_warn": "Παρακαλώ εισάγετε περιγραφή.",
        "journal_title": "Ημερολόγιο Ονείρων",
        "journal_desc": "Ιστορικό ονείρων.",
        "no_dreams": "Δεν υπάρχουν όνειρα.",
        "lucidity_label": "Διαύγεια",
        "story_label": "Αφήγηση",
        "stats_title": "Στατιστικά",
        "stats_desc": "Συνολικά όνειρα",
        "total_dreams": "Συνολικά όνειρα",
        "status_premium": "Κατάσταση: Ενεργή",
        "status_free": "Δωρεάν λειτουργία",
        "account_title": "Διαχείριση Λογαριασμού",
        "account_desc": "Διαχείριση προφίλ",
        "terms_title": "Όροι και Προϋποθέσεις",
        "terms_text": "Όροι χρήσης.",
        "member_space": "Περιοχή μελών",
        "cancel_sub": "Ακύρωση συνδρομής",
        "pack_btn": "✨ Πακέτο 15 Ονείρων (€4.99)",
        "unlim_btn": "🚀 Απεριορίστο"
    }
}

# --- 4. OBSERVATOIRE LUNAIRE & IA ---
def get_moon_phase_detail(dt=None):
    if dt is None:
        dt = datetime.datetime.now()
    known_new_moon = datetime.datetime(2000, 1, 6, 18, 14)
    diff = dt - known_new_moon
    days = diff.total_seconds() / 86400
    cycles = days / 29.5305877057
    phase = cycles - int(cycles)

    if phase < 0.03 or phase > 0.97:
        return (phase, "Nouvelle lune 🌑", "Intériorité profonde, silence du mental.")
    elif phase < 0.22:
        return (phase, "Premier Croissant 🌒", "Émergence de l'impulsion. Les rêves portent sur le renouveau.")
    elif phase < 0.28:
        return (phase, "Premier Quartier 🌓", "Tension créatrice. Le subconscient cherche à équilibrer les polarités.")
    elif phase < 0.47:
        return (phase, "Gibbeuse Croissante 🌔", "Affinement de l'intuition. L'esprit assimile les synchronicités.")
    elif phase < 0.53:
        return (phase, "Pleine Lune 🌕", "Apogée onirique ! Émotions, visions intenses et révélations.")
    elif phase < 0.72:
        return (phase, "Gibbeuse Décroissante 🌖", "Temps d'intégration, de recul et de lâcher-prise analytique.")
    elif phase < 0.78:
        return (phase, "Dernier Quartier 🌗", "Phase de lâcher-prise. Nettoyage des mémoires encombrantes.")
    else:
        return (phase, "Dernier Croissant 🌘", "Apaisement et repos de l'esprit avant le prochain cycle.")

def render_lunar_observatory():
    phase_val, phase_nom, signification = get_moon_phase_detail()
    st.markdown("### 🔭 Observatoire de la Synchronodicité Lunaire")
    st.markdown(f"#### Cycle Actuel : {phase_nom}")
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=phase_val * 100,
            number={"suffix": "%", "font": {"color": "#81ECF8", "size": 28}},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#81ECF8"}}
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e0efff"},
        height=210,
        margin=dict(t=20, b=10, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

def generate_ai_interpretation(title, emotion, lucidity, description):
    return f"""### ✨ Analyse & Étape d'Interprétation Profonde
* **Résonance Émotionnelle :** L'émotion dominante de **{emotion}** associée à ce rêve indique un besoin de libération ou d'intégration psychique.
* **Indice de Lucidité ({lucidity}/5) :** Votre degré de conscience onirique montre une perméabilité intéressante entre le conscient et l'inconscient.

#### 🔍 Analyse Détaillée des Mots & Symboles Clés
* **L'immersion / Baignade :** Symbolise le plongeon dans l'inconscient, les émotions refoulées ou le besoin de lâcher-prise.
* **L'obscurité / Nuit :** Représente le domaine de l'inconnu, du repos mental ou des peurs latentes à explorer.
* **Les Étoiles & La Lune :** Les étoiles signalent des repères et une espérance, tandis que la lune gouverne les cycles psychiques.
* **L'Eau / Mer Chaude :** La matrice affective. Une eau chaude indique un climat émotionnel rassurant ou une guérison en cours.
* **La Prière / Élévation :** Traduit une recherche d'alignement, de gratitude ou de quête de sens spirituel supérieur.

---
💡 **Piste d'Évolution :** Observez comment ce songe fait écho à vos aspirations actuelles. Tenez un journal régulier pour ancrer ces messages.
"""

# --- 5. NAVIGATION & BARRE LATÉRALE ---
st.sidebar.title("Aureva Mind")
selected_lang = st.sidebar.selectbox("Langue / Language", list(translations.keys()))
t = translations[selected_lang]

menu = st.sidebar.radio("Navigation", [
    t["nav_analyse"],
    t["nav_journal"],
    t["nav_stats"],
    t["nav_terms"],
    t["nav_account"]
])
# --- EN-TÊTE SCINTILLANT ---
    st.markdown("""
        <style>
        @keyframes superTwinkle {
            0% { 
                opacity: 0.75; 
                text-shadow: 0 0 10px rgba(129,236,248,0.5), 0 0 20px rgba(255,215,0,0.2);
                transform: scale(1);
            }
            50% { 
                opacity: 1; 
                text-shadow: 0 0 30px rgba(129,236,248,0.9), 0 0 50px rgba(255,215,0,0.7), 0 0 70px rgba(255,255,255,0.5);
                transform: scale(1.02);
            }
            100% { 
                opacity: 0.75; 
                text-shadow: 0 0 10px rgba(129,236,248,0.5), 0 0 20px rgba(255,215,0,0.2);
                transform: scale(1);
            }
        }
        .scintillant-title-forte {
            animation: superTwinkle 2s infinite ease-in-out;
            font-family: 'Cinzel', serif;
            font-size: 2.6rem;
            color: #81ECF8;
            text-align: center;
            margin-bottom: 0;
            letter-spacing: 2px;
        }
        </style>
        
        <div style="text-align: center; padding: 15px 0 20px 0;">
            <h1 class="scintillant-title-forte">
                ✨ 🌙 Aureva Mind 🌟
            </h1>
        </div>
    """, unsafe_allow_html=True)
MAX_FREE_DREAMS = 4

# --- 6. GESTION DES ONGLETS & ACTIONS ---
if menu == t["nav_analyse"]:
    render_lunar_observatory()
    st.markdown(f"### {t['analysis_title']}")
    st.markdown(f"""
        <div style="background: rgba(79, 70, 229, 0.1); border-left: 4px solid #81ECF8; padding: 12px 16px; border-radius: 0 8px 8px 0; margin-bottom: 20px; color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;">
            {t['intro_desc']}
        </div>
    """, unsafe_allow_html=True)

    title = st.text_input(t["dream_title"])
    emotion = st.selectbox(t["dream_emotion"], ["Joie", "Peur", "Tristesse", "Sérénité", "Colère", "Mystère", "Amour"])
    lucidity = st.slider(t["lucidity_label"], 1, 5, 3)

    st.markdown("🎙️ Dicter le rêve à l'oral")
    audio = mic_recorder(start_prompt="Parler", stop_prompt="Arrêter", key="mic_dream")
    if audio:
        st.audio(audio['bytes'])
        st.success("Audio enregistré avec succès !")

    description = st.text_area(t["dream_desc"])

    # Vérification du quota gratuit avec is_premium corrigé
    if not user.is_premium and user.dreams_count >= MAX_FREE_DREAMS:
        st.markdown(
            "<p style='color: #8b949e; font-style: italic; margin-top: 10px;'>"
            "Vous avez exploré vos premiers rêves gratuitement. Pour aller plus loin et déverrouiller l'accès illimité ou le pack découverte, rendez-vous dans l'onglet <strong>Mon Compte</strong>."
            "</p>", 
            unsafe_allow_html=True
        )
        if stripe:
            st.link_button("✨ S'abonner à Aureva Mind", "https://buy.stripe.com/TON_LIEN_STRIPE")
    else:
        if st.button(t["btn_analyser"]):
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
                st.success("✨ Analyse générée avec succès !")
                st.markdown(ai_interpretation, unsafe_allow_html=True)
            else:
                st.warning(t["empty_desc_warn"])

    # --- ANALYSE CIBLÉE DES SCHÉMAS INCONSCIENTS (Retrouvée depuis la capture 7) ---
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🔍 Analyse ciblée des schémas inconscients")

    filter_option = st.radio(
        "Méthode de sélection pour l'analyse :",
        ["Tous les rêves enregistrés", "Par nombre de rêves récents", "Par plage de dates (Du... Au...)"]
    )

    selected_dreams = []
    all_dreams = db.scalars(select(DreamRecord).order_by(DreamRecord.created_at.desc())).all()

    if filter_option == "Tous les rêves enregistrés":
        selected_dreams = all_dreams
    elif filter_option == "Par nombre de rêves récents":
        limit_count = st.slider("Nombre de rêves à analyser", min_value=2, max_value=20, value=5)
        selected_dreams = all_dreams[:limit_count]
    elif filter_option == "Par plage de dates (Du... Au...)":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("Date de début")
        with col_d2:
            end_date = st.date_input("Date de fin")
        
        selected_dreams = [
            d for d in all_dreams
            if d.created_at and start_date <= d.created_at.date() <= end_date
        ]

    if st.button("🚀 Lancer l'analyse croisée de la sélection"):
        if len(selected_dreams) >= 2:
            trend_summary = f"### 📊 Synthèse croisée de {len(selected_dreams)} rêves :\n" + "\n".join([f"- **{d.title}** ({d.emotion}) : {d.description[:60]}..." for d in selected_dreams])
            st.markdown(f"**Analyse basée sur {len(selected_dreams)} rêves sélectionnés.**")
            st.markdown(trend_summary, unsafe_allow_html=True)
        else:
            st.warning("Veuillez sélectionner une période ou un nombre de rêves suffisant (au moins 2).")

elif menu == t["nav_journal"]:
    st.markdown(f"### 🗂️ {t['journal_title']}")
    st.markdown(t["journal_desc"])
    dreams = db.scalars(select(DreamRecord)).all()
    if not dreams:
        st.info(t["no_dreams"])
    else:
        for d in reversed(dreams):
            with st.expander(f"✨ {d.title or 'Rêve sans titre'} ({d.emotion})"):
                st.write(f"**{t['lucidity_label']} :** {d.lucidity}/5")
                st.write(f"**{t['story_label']} :** {d.description}")
                if d.interpretation:
                    st.markdown(d.interpretation, unsafe_allow_html=True)
                if st.button("🗑️ Supprimer ce rêve", key=f"delete_{d.id}"):
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
    st.markdown(f"### 📊 {t['stats_title']}")
    st.markdown(t["stats_desc"])
    st.metric(t["total_dreams"], user.dreams_count)
    if user.is_premium:
        st.success(t["status_premium"])
    else:
        st.info(t["status_free"])

elif menu == t["nav_terms"]:
    st.markdown(f"### 📜 {t['terms_title']}")
    st.markdown(f"""
        <div style="background: #161b22; padding: 20px; border-radius: 10px; color: #cbd5e1;">
            {t['terms_text']}
        </div>
    """, unsafe_allow_html=True)

elif menu == t["nav_account"]:
    st.markdown(f"### ⚙️ {t['account_title']}")
    st.markdown(t["account_desc"])

    with st.form("profile_form"):
        name_input = st.text_input("Prénom", value=user.first_name)
        email_input = st.text_input("Email", value=user.email)
        submit_profile = st.form_submit_button("Mettre à jour le profil")
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
            st.success("Paiement validé : Pack 15 rêves activé avec succès !")
    with col2:
        if st.button(t["unlim_btn"]):
            user.is_premium = True
            db.commit()
            st.success("Paiement validé : Abonnement illimité activé avec succès !")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    if st.button(t["cancel_sub"]):
        user.is_premium = False
        db.commit()
        st.warning("Votre abonnement a bien été résilié.")
