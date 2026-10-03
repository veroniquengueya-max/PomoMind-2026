"""UI text for every language. Pure data: no Streamlit imports.

Rules:
- Every key must exist in every language (tests enforce this).
- Use {placeholders} for dynamic values, filled via t("key", name=value).
- Keys are namespaced by screen: login.*, sidebar.*, professor.*, student.*, ...
"""

STRINGS = {
    "en": {
        "role.Student":"Student",
        "role.Professor": "Professor",
        "language.label": "Select Language / Choisir Langue",
        # login
        "login.title": "🔒 PomoMind AI - Portal",
        "login.subtitle": "Please choose your profile to access your secure space.",
        "login.role": "🔑 Select your role :",
        "login.username": "Username / Email",
        "login.password": "Password",
        "login.button": "Login",
        "login.welcome": "🔒 Welcome !",
        "login.error": "❌ Invalid username, password or role.",
        # sidebar
        "sidebar.title": "👤 {role} Area",
        "sidebar.streak": "🔥 Study Streak",
        "sidebar.streak_value": "3 days",
        "sidebar.score": "✨ Global Score",
        "sidebar.demo_mode": "⚙️ Demo Mode (No API Key)",
        "sidebar.api_key": "Gemini API Key:",
        "sidebar.logout": "🚪 Logout",
        # professor
        "professor.title": "👨‍🏫 Teacher Dashboard - Specialty: {subject}",
        "professor.intro": "Send your official course materials to the class.",
        "professor.uploader": "Drag and drop your official course material (PDF):",
        "professor.broadcast": "🖲️ Broadcast the class course",
        "professor.spam": "⚠️ Anti-Spam: Please wait 10 seconds.",
        "professor.missing_key": "⚠️ Please set up your Gemini API key on the left.",
        "professor.missing_pdf": "⚠️ Please select a PDF file.",
        "professor.spinner": "The AI agent is verifying the course...",
        "professor.success": "✅ The {subject} course has been successfully broadcasted!",
        "professor.blocked": "🛑 AI blocked the broadcasting! {reason}",
        "professor.error": "Error: {error}",
        # student
        "student.title": "🧠 PomoMind Social Network",
        "student.notification": "🔔 **Teacher Notification:** A new official course of **{subject}** has been broadcasted by *'{filename}'*",
        "student.tab_timer": "⏳ Pomodoro Timer & Music",
        "student.tab_feed": "📱 Course Feed",
        # timer
        "timer.subheader": "📈 Pomodoro Focus Session",
        "timer.sound": "🎵 Sound atmosphere :",
        "sound.silence": "Silence",
        "sound.lofi": "Lo-Fi study",
        "sound.binaural": "Binaural Waves",
        "timer.start": "⏱️ Start the Session (10s)",
        "timer.focus": "Stay focused...",
        "timer.done": "🎉 Session validated! +50 XP",
        # feed
        "feed.subheader": "📚 Official Course Feed",
        "feed.document": "📄 **Shared document:** {filename} ({subject})",
        "feed.flashcards_button": "Transform the document into Flashcards",
        "feed.missing_key": "⚠️ Please set up your Gemini API key on the left to enable the AI.",
        "feed.spinner": "The AI agent is slicing your course into TikTok Flashcards...",
        "feed.success": "📱 Flashcards successfully generated! +20 XP",
        "feed.error": "AI error: {error}",
        "feed.empty": "No official document has been shared.",
    },
    "fr": {
        "role.Student": "Étudiant(e)",
        "role.Professor": "Professeur(e)",
        "language.label": "Select Language / Choisir Langue",
        # login
        "login.title": "🔒 PomoMind AI - Portail",
        "login.subtitle": "Veuillez choisir votre profil pour accéder à votre espace sécurisé.",
        "login.role": "🔑 Choisis ton profil :",
        "login.username": "Identifiant / Email",
        "login.password": "Mot de Passe",
        "login.button": "Se connecter",
        "login.welcome": "🔒 Bienvenue !",
        "login.error": "❌ Identifiant, mot de passe ou rôle incorrect.",
        # sidebar
        "sidebar.title": "👤 Espace {role}",
        "sidebar.streak": "🔥 Série d'étude",
        "sidebar.streak_value": "3 Jours",
        "sidebar.score": "✨ Score global",
        "sidebar.demo_mode": "⚙️ Mode Démo (Sans clé API)",
        "sidebar.api_key": "Clé API Gemini:",
        "sidebar.logout": "🚪 Déconnexion",
        # professor
        "professor.title": "👨‍🏫 Tableau de Bord Enseignant - Spécialité: {subject}",
        "professor.intro": "Envoyez vos supports de cours officiels à la classe.",
        "professor.uploader": "Glissez et déposez le cours officiel (Format PDF) :",
        "professor.broadcast": "🖲️ Diffusez le cours de la classe",
        "professor.spam": "⚠️ Anti-Spam: Veuillez attendre 10 secondes.",
        "professor.missing_key": "⚠️ Veuillez configurer votre clé API Gemini à gauche.",
        "professor.missing_pdf": "⚠️ Veuillez sélectionner un fichier PDF.",
        "professor.spinner": "L'agent IA vérifie le cours...",
        "professor.success": "✅ Le cours de {subject} a été diffusé avec succès!",
        "professor.blocked": "🛑 Diffusion bloquée par l'IA! {reason}",
        "professor.error": "Erreur : {error}",
        # student
        "student.title": "🧠 PomoMind Social Network",
        "student.notification": "🔔 **Notification Enseignant :** Un nouveau cours officiel de **{subject}** a été diffusé par *'{filename}'*",
        "student.tab_timer": "⏳ Chrono Pomodoro & Musique",
        "student.tab_feed": "📱 Flux de cours",
        # timer
        "timer.subheader": "📈 Session Focus Pomodoro",
        "timer.sound": "🎵 Ambiance sonore :",
        "sound.silence": "Silence",
        "sound.lofi": "Lo-Fi study",
        "sound.binaural": "Ondes Binaurales",
        "timer.start": "⏱️ Lancer ma session d'étude (10s)",
        "timer.focus": "Reste concentré...",
        "timer.done": "🎉 Session validée! +50 XP",
        # feed
        "feed.subheader": "📚 Flux de cours officiel.",
        "feed.document": "📄 **Document partagé :** {filename} ({subject})",
        "feed.flashcards_button": "🖲️ Transformer le document en Flashcards",
        "feed.missing_key": "⚠️ Veuillez configurer votre clé API Gemini à gauche pour activer le cerveau de l'IA.",
        "feed.spinner": "L'agent IA PomoMind découpe ton cours en Flashcards TikTok...",
        "feed.success": "📱 Flashcards générées avec succès ! +20 XP",
        "feed.error": "Erreur IA : {error}",
        "feed.empty": "Aucun document officiel n'a été partagé.",
    },
}
