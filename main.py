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

# Style CSS : Nuit étoilée pour l'app et texte NOIR dans les boîtes de résultats/alertes
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #090a0f, #1b1e3b, #090a0f) !important;
        color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0f111a !important;
    }
    h1, h2, h3, p, label, span, div {
        color: #f1f5f9 !important;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        color: #ffffff !important;
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
    }
    /* Boîtes de succès, infos et alertes avec fond clair et ÉCRITURE NOIRE */
    div[data-baseweb="notification"], .stAlert {
        background-color: #f8fafc !important;
        color: #0f111a !important;
        border: 1px solid #cbd5e1 !important;
    }
    .stAlert p, .stAlert span, .stAlert div, div[data-baseweb="notification"] p {
        color: #0f111a !important;
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

# --- 3. DICTIONNAIRE DES 10 LANGUES ---
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
        "btn_analyze": "Analyser mon rêve",
        "member_space": "⚙️ Espace Membre",
        "cancel_sub": "❌ Résilier l'abonnement",
        "manage_account": "📝 S'inscrire / Gérer mon compte",
        "premium_title": "🌙 Aureva Mind Premium",
        "premium_desc": "Débloquez tout le potentiel de vos rêves :",
        "pack_btn": "✨ Pack 15 rêves (4,99 €)",
        "unlim_btn": "🚀 Illimité (12 €/mois)"
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
        "btn_analyze": "Analyze my dream",
        "member_space": "⚙️ Member Space",
        "cancel_sub": "❌ Cancel subscription",
        "manage_account": "📝 Register / Manage account",
        "premium_title": "🌙 Aureva Mind Premium",
        "premium_desc": "Unlock the full potential of your dreams:",
        "pack_btn": "✨ 15 Dreams Pack (€4.99)",
        "unlim_btn": "🚀 Unlimited (€12/month)"
    },
    "Español": {
        "nav_title": "Navegación",
        "nav_space": "Mi Espacio",
        "nav_analyze": "Analizar un sueño",
        "nav_terms": "Términos y Condiciones",
        "profile_title": "👤 Mi Perfil",
        "profile_name": "Tu nombre",
        "lang_title": "🌍 Idioma",
        "lang_select": "Elige tu idioma",
        "journal_titre": "📖 Diario de Sueños",
        "journal_desc": "Encuentra el historial de tus análisis.",
        "stats_titre": "📊 Estadísticas y Estado",
        "stats_desc": "Sigue tu actividad onírica.",
        "analysis_title": "✨ Nuevo Análisis Onírico",
        "terms_title": "📜 Términos y Condiciones de Uso y Venta",
        "btn_analyze": "Analizar mi sueño",
        "member_space": "⚙️ Zona de Miembros",
        "cancel_sub": "❌ Cancelar suscripción",
        "manage_account": "📝 Registrarse / Gestionar cuenta",
        "premium_title": "🌙 Aureva Mind Premium",
        "premium_desc": "Desbloquea todo el potencial de tus sueños:",
        "pack_btn": "✨ Pack 15 sueños (4,99 €)",
        "unlim_btn": "🚀 Ilimitado (12 €/mes)"
    },
    "Deutsch": {
        "nav_title": "Navigation",
        "nav_space": "Mein Bereich",
        "nav_analyze": "Traum analysieren",
        "nav_terms": "AGB",
        "profile_title": "👤 Mein Profil",
        "profile_name": "Ihr Vorname",
        "lang_title": "🌍 Sprache",
        "lang_select": "Wählen Sie Ihre Sprache",
        "journal_titre": "📖 Traumtagebuch",
        "journal_desc": "Finden Sie Ihre Traumanalysen.",
        "stats_titre": "📊 Statistik & Status",
        "stats_desc": "Verfolgen Sie Ihre Traumaktivität.",
        "analysis_title": "✨ Neue Traumanalyse",
        "terms_title": "📜 Allgemeine Geschäftsbedingungen",
        "btn_analyze": "Meinen Traum analysieren",
        "member_space": "⚙️ Mitgliedsbereich",
        "cancel_sub": "❌ Abonnement kündigen",
        "manage_account": "📝 Registrieren / Konto verwalten",
        "premium_title": "🌙 Aureva Mind Premium",
        "premium_desc": "Entfalten Sie das volle Potenzial Ihrer Träume:",
        "pack_btn": "✨ 15 Träume-Paket (4,99 €)",
        "unlim_btn": "🚀 Unbegrenzt (12 €/Monat)"
    },
    "Italiano": {
        "nav_title": "Navigazione",
        "nav_space": "Il Mio Spazio",
        "nav_analyze": "Analizza un sogno",
        "nav_terms": "Termini e Condizioni",
        "profile_title": "👤 Il Mio Profilo",
        "profile_name": "Il tuo nome",
        "lang_title": "🌍 Lingua",
        "lang_select": "Scegli la tua lingua",
        "journal_titre": "📖 Diario dei Sogni",
        "journal_desc": "Trova la cronologia delle tue analisi.",
        "stats_titre": "📊 Statistiche e Stato",
        "stats_desc": "Monitora la tua attività onirica.",
        "analysis_title": "✨ Nuova Analisi Onirica",
        "terms_title": "📜 Termini e Condizioni di Uso e Vendita",
        "btn_analyze": "Analizza il mio sogno",
        "member_space": "⚙️ Area Membri",
        "cancel_sub": "❌ Annulla abbonamento",
        "manage_account": "📝 Registrati / Gestisci account",
        "premium_title": "🌙 Aureva Mind Premium",
        "premium_desc": "Sblocca tutto il potenziale dei tuoi sogni:",
        "pack_btn": "✨ Pacchetto 15 Sogni (4,99 €)",
        "unlim_btn": "🚀 Illimitato (12 €/mese)"
    },
    "Português": {
        "nav_title": "Navegação",
        "nav_space": "Meu Espaço",
        "nav_analyze": "Analisar um sonho",
        "nav_terms": "Termos e Condições",
        "profile_title": "👤 Meu Perfil",
        "profile_name": "Seu primeiro nome",
        "lang_title": "🌍 Idioma",
        "lang_select": "Escolha seu idioma",
        "journal_titre": "📖 Diário de Sonhos",
        "journal_desc": "Encontre o histórico das suas análises.",
        "stats_titre": "📊 Estatísticas e Status",
        "stats_desc": "Acompanhe sua atividade onírica.",
        "analysis_title": "✨ Nova Análise Onírica",
        "terms_title": "📜 Termos e Condições de Uso e Venda",
        "btn_analyze": "Analisar meu sonho",
        "member_space": "⚙️ Área de Membros",
        "cancel_sub": "❌ Cancelar assinatura",
        "manage_account": "📝 Cadastrar / Gerenciar conta",
        "premium_title": "🌙 Aureva Mind Premium",
        "premium_desc": "Desbloqueie todo o potencial dos seus sonhos:",
        "pack_btn": "✨ Pacote 15 Sonhos (€4,99)",
        "unlim_btn": "🚀 Ilimitado (€12/mês)"
    },
    "Nederlands": {
        "nav_title": "Navigatie",
        "nav_space": "Mijn Ruimte",
        "nav_analyze": "Analyseer een droom",
        "nav_terms": "Algemene Voorwaarden",
        "profile_title": "👤 Mijn Profiel",
        "profile_name": "Jouw voornaam",
        "lang_title": "🌍 Taal",
        "lang_select": "Kies je taal",
        "journal_titre": "📖 Droomdagboek",
        "journal_desc": "Bekijk de geschiedenis van je dromen.",
        "stats_titre": "📊 Statistieken & Status",
        "stats_desc": "Volg je droomactiviteit.",
        "analysis_title": "✨ Nieuwe Droomanalyse",
        "terms_title": "📜 Algemene Voorwaarden voor Gebruik en Verkoop",
        "btn_analyze": "Analyseer mijn droom",
        "member_space": "⚙️ Ledenruimte",
        "cancel_sub": "❌ Abonnement opzeggen",
        "manage_account": "📝 Registreren / Beheer account",
        "premium_title": "🌙 Aureva Mind Premium",
        "premium_desc": "Ontgrendel het volledige potentieel van je dromen:",
        "pack_btn": "✨ 15 Dromen Pakket (€4,99)",
        "unlim_btn": "🚀 Onbeperkt (€12/maand)"
    },
    "Polski": {
        "nav_title": "Nawigacja",
        "nav_space": "Moja Przestrzeń",
        "nav_analyze": "Analizuj sen",
        "nav_terms": "Regulamin",
        "profile_title": "👤 Mój Profil",
        "profile_name": "Twoje imię",
        "lang_title": "🌍 Język",
        "lang_select": "Wybierz język",
        "journal_titre": "📖 Dziennik Snów",
        "journal_desc": "Znajdź historię swoich analiz.",
        "stats_titre": "📊 Statystyki i Status",
        "stats_desc": "Śledź swoją aktywność.",
        "analysis_title": "✨ Nowa Analiza Snu",
        "terms_title": "📜 Regulamin i Warunki Korzystania",
        "btn_analyze": "Analizuj mój sen",
        "member_space": "⚙️ Strefa Członka",
        "cancel_sub": "❌ Anuluj subskrypcję",
        "manage_account": "📝 Zarejestruj się / Zarządzaj",
        "premium_title": "🌙 Aureva Mind Premium",
        "premium_desc": "Odblokuj pełny potencjał swoich snów:",
        "pack_btn": "✨ Pakiet 15 Snów (4,99 €)",
        "unlim_btn": "🚀 Nieograniczony (12 €/miesiąc)"
    },
    "Русский": {
        "nav_title": "Навигация",
        "nav_space": "Мое Пространство",
        "nav_analyze": "Анализ сна",
        "nav_terms": "Условия использования",
        "profile_title": "👤 Мой Профиль",
        "profile_name": "Ваше имя",
        "lang_title": "🌍 Язык",
        "lang_select": "Выберите язык",
        "journal_titre": "📖 Дневник снов",
        "journal_desc": "История ваших сновидений.",
        "stats_titre": "📊 Статистика и Статус",
        "stats_desc": "Отслеживайте вашу активность.",
        "analysis_title": "✨ Новый Анализ Сна",
        "terms_title": "📜 Условия использования и продажи",
        "btn_analyze": "Анализировать мой сон",
        "member_space": "⚙️ Кабинет участника",
        "cancel_sub": "❌ Отменить подписку",
        "manage_account": "📝 Регистрация / Аккаунт",
        "premium_title": "🌙 Aureva Mind Premium",
        "premium_desc": "Раскройте весь потенциал ваших снов:",
        "pack_btn": "✨ Пакет 15 снов (4,99 €)",
        "unlim_btn": "🚀 Безлимит (12 €/месяц)"
    },
    "日本語": {
        "nav_title": "ナビゲーション",
        "nav_space": "マイ空間",
        "nav_analyze": "夢を分析する",
        "nav_terms": "利用規約",
        "profile_title": "👤 マイプロフィール",
        "profile_name": "お名前",
        "lang_title": "🌍 言語",
        "lang_select": "言語を選択",
        "journal_titre": "📖 夢のジャーナル",
        "journal_desc": "夢の分析履歴を表示します。",
        "stats_titre": "📊 統計とステータス",
        "stats_desc": "夢の活動を追跡します。",
        "analysis_title": "✨ 新しい夢の分析",
        "terms_title": "📜 利用規約および販売条件",
        "btn_analyze": "夢を分析する",
        "member_space": "⚙️ 会員スペース",
        "cancel_sub": "❌ 定期購入を解約",
        "manage_account": "📝 登録 / アカウント管理",
        "premium_title": "🌙 Aureva Mind プレミアム",
        "premium_desc": "夢の可能性を最大限に引き出す：",
        "pack_btn": "✨ 15夢パック (4.99 €)",
        "unlim_btn": "🚀 無制限 (12 €/月)"
    }
}

# --- 4. BARRE LATÉRALE ---
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
        ["Français", "English", "Español", "Deutsch", "Italiano", "Português", "Nederlands", "Polski", "Русский", "日本語"]
    )
    t = translations[langue]

    st.markdown("---")
    st.title(t["nav_title"])
    page = st.radio("Aller à", [t["nav_space"], t["nav_analyze"], t["nav_terms"]])

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

    st.markdown("---")
    st.subheader(t["premium_title"])
    st.write(t["premium_desc"])

    st.link_button(t["pack_btn"], "https://buy.stripe.com/9B68wQ9el5I21L1djxaIM00", use_container_width=True)
    st.link_button(t["unlim_btn"], "https://buy.stripe.com/fZu14o4Y53zUcpFenBaIM01", use_container_width=True)

# --- 5. CORPS PRINCIPAL DE L'APPLICATION ---
if page == t["nav_space"]:
    st.title(f"Bienvenue, {user.first_name} 🌙")
    
    # Onglets renommés proprement (plus de "Analyse IA")
    tab1, tab2, tab3 = st.tabs(["✨ Analyser", "📖 Journal", "📊 Statistiques"])
    
    with tab1:
        st.subheader(t["analysis_title"])
        dream_title = st.text_input("Titre de votre rêve")
        dream_emotion = st.selectbox("Émotion principale", ["Joie", "Peur", "Tristesse", "Mystère", "Aventure", "Autre"])
        dream_lucidity = st.slider("Niveau de lucidité (1 à 5)", 1, 5, 2)
        dream_desc = st.text_area("Racontez votre rêve en détail...")

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

                # Ces blocs s'afficheront désormais avec un fond clair et une écriture noire bien lisible
                st.success("✨ Analyse onirique réalisée avec succès !")
                st.markdown(f"### 🌌 Interprétation profonde pour {user.first_name}")
                
                if dream_emotion == "Joie":
                    analyse_texte = "Ce rêve traduit une libération émotionnelle positive et une grande harmonie intérieure. Votre subconscient célèbre une réussite ou un apaisement récent."
                elif dream_emotion == "Peur":
                    analyse_texte = "L'apparition de cette peur dans votre songe met en lumière un défi ou une transition que vous affrontez actuellement. C'est l'occasion de libérer des tensions accumulées."
                elif dream_emotion == "Mystère":
                    analyse_texte = "Ce rêve cache des symboles profonds liés à votre intuition. Votre esprit cherche à résoudre une énigme ou explore des dimensions inconscientes."
                else:
                    analyse_texte = f"Dominé par l'émotion de **{dream_emotion}**, ce rêve révèle un besoin d'expression et d'écoute de vos aspirations intimes."

                st.info(f"{analyse_texte}\n\n*Niveau de lucidité estimé à {dream_lucidity}/5 :* {'Vous aviez un bon contrôle de vos actions oniriques.' if dream_lucidity >= 3 else 'Votre rêve était principalement guidé par le flux de votre inconscient.'}")
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
    st.write("Rendez-vous dans l'onglet 'Mon Espace > Analyser' pour soumettre votre rêve.")

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
