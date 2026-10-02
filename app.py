from cProfile import label
import hashlib
import streamlit as st
import google as genai
import time

st.set_page_config(page_title = "PomoMind AI - Secure Login", page_icon = "🔒")
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "Student"
if "username"  not in st.session_state:
    st.session_state["username"] = ""
if "subject" not in st.session_state:
    st.session_state["subject"] = None
if "xp" not in st.session_state:
    st.session_state["xp"] = 150
if "prof_pdf_name" not in st.session_state:
    st.session_state["prof_pdf_name"] = None
if "prof_pdf_subject" not in st.session_state:
    st.session_state["prof_pdf_subject"] = None
if "dernier_clic_prof" not in st.session_state:
    st.session_state["dernier_clic_prof"] = 0.0

language = st.sidebar.selectbox("Select Language", ["English", "French"])

TRADUCTIONS = {
    "French": {
        "title": "🔒 PomoMind AI - Portail Educatif",
        "subtitle": "Veuillez choisir votre profile pour accéder àbotre espace sécurisé.",
        "radio_label": "🔑 choisis ton profil :",
        "user_label": "Identifiant / Email",
        "pass_label": "Mot de Passe",
        "btn_login": "Se connecter",
        "err_role": "❌ Le rôle sélectionné ne pas à vos droit d'accés",
        "err_credentials": "❌ Identifiant ou mot de passe incorrect.",
        "welcome_prof": "🔒 Bienvenue Professeur de",
        "welcome_student": "🔒 Bienvenue Etudiant !",
        "logout": "🚪 Déconnexion",
        "streak_label": "🔥 Série d'étude",
        "xp_label": "✨ Score global"
    },
    "English": {
       "title": "🔒 PomoMind AI - Educational Portal",
              "subtitle": "Please choose your profile to access your secure space.",
              "radio_label": "🔑 Select your role :",
              "user_label": "Username / Email",
              "pass_label": "Password",
              "btn_login": "Login",
              "err_role": "❌ The selected role doesn't match your access rights",
              "err_credentials": "❌ Invalid username or password.",
              "welcome_prof": "🔒 Welcome Professor of",
              "welcome_student": "🔒 Wecome Student!",
              "logout": "🚪 Logout",
              "streak_label": "🔥 Study Streak",
              "xp_label": "✨ Global Score"
    }
}
txt = TRADUCTIONS[language]
def hacher_mot_de_passe(password_string):
    return hashlib.sha256(password_string.encode('utf-8')).hexdigest()
USERS = {
    "student": {
        "password" : hacher_mot_de_passe("student123"),
        "role": "Student",
        "subject": None
    },
    "prof_bio": {
        "password" : hacher_mot_de_passe("prof_bio123"),
        "role": "Professor",
        "subject": "Biologie"
    },
    "prof_cyber": {
        "password" : hacher_mot_de_passe("prof_cyber123"),
        "role": "Professor",
        "subject": "Cybersecurity"
    },
}
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title(txt["title"])
    st.write(txt["subtitle"])

    role_choice = st.radio(txt["radio_label"], ["Ètudiant (Student)", "Professor (Professor)"])
    username_input = st.text_input(txt["user_label"], placeholder="student, prof_bio or prof_cyber")
    password_input = st.text_input(txt["pass_label"], type="password")

    if st.button(txt["btn_login"]):
        if username_input in USERS: 
            user_data = USERS[username_input]

            if hacher_mot_de_passe(password_input) == user_data["password"]:
                if "Professeur" in role_choice and user_data["role"] == "Professor":
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = "Professor"
                    st.session_state["username"] = username_input
                    st.session_state["subject"] = user_data["subject"]
                    st.success(f"{txt['welcome_prof']} {user_data['subject']} !" if language == "French" else f"{txt['welcome_prof']} {user_data['subject']}")
                    st.rerun()
            elif "Ètudiant" in role_choice and user_data["role"] == "Student":
                  st.session_state["logged_in"] = True
                  st.session_state["role"] = "Student"
                  st.session_state["username"] = username_input
                  st.success(txt["welcome_student"])
            else:
                st.error(txt["err_role"])
        else:
            st.error(txt["err_credentials"])
    else: 
        st.error(txt["err_credentials"])
else:
    st.sidebar.title(f"👤 Espace {st.session_state.role}")

    if st.session_state.role == "Student":
        st.sidebar.metric(label=txt["streak_label"], value="3 Jour" if language == "French" else "3 days")
        st.sidebar.metric(label=txt["xp_label"], value=f"{st.session_state.xp} XP")

    api_key_input = st.sidebar.text_input("Clé API Gemini: ", type="password", placeholder="AQAbrtA...")

    if st.sidebar.button(txt["logout"]):
        st.session_state.clear()
        st.rerun()
    if st.session_state.role == "Professor":
        st.title(f"👨‍🏫 Tableau de Bord Enseignant - Spécialité: {st.session_state.subject  if language == 'French' else st.session_state.subject}")
        st.write("Envoyez vos supports de cours officiels à la classe." if language == "French" else "Send your offical course materials to the class.")

        uploaded_pdf = st.file_uploader("Glissez et déposez le cours officiel (Format PDF) :", type=["pdf"] if language == "French" else "Drag and drop your official course material (PDF Format):")

        if st.button("🖲️ Diffusez le cours de la classe if language == 'French' else 'Broadcast the class course'"):
            temps_actuel = time.time()
            temps_ecoule = temps_actuel - st.session_state["dernier_clic_prof"]

            if temps_ecoule < 10:
                st.warning(f"⚠️ Anti-Spam: Veuillez attendre 10 secondes avant de diffuser à nouveau le cours." if language == "French" else f" ⚠️ Anti-Spam: Please wait 10 seconds before broadcasting the course again.")
            elif not api_key_input:
                st.error(f"⚠️ Veuillez configurer votre clé API Gemini à gauche pour activer le filtre IA." if language == "French" else f"⚠️ Please set up your Gemini API key on the left to enable the AI filter.")
            elif uploaded_pdf is not None:
                with st.spinner("L'agent IA vérifie la confirmation du cours..." if language == "French" else "The AI agent is verifying the course confirmation..."):
                    try:
                        client = genai.Client(api_key=api_key_input)
                        pdf_bytes = uploaded_pdf.read()

                        prompt_controle = f"""
                        Tu es l'agent de sécurité de PomoMind AI. Rôle: Vérifier que le document correspond à : {st.session_state.subject}.
                        Téponds UNIQUEMENT par [VALIDE] ou [INVALIDE: Raison]
                        """
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents = [prompt_controle, {"data": pdf_bytes, "mime_type": "application/pdf"}]
                        )
                        if "[VALIDE]" in response.text:
                            st.session_state["dernier_clic_prof"] = temps_actuel
                            st.session_state["prof_pdf_name"] = uploaded_pdf.name
                            st.session_state["prof_pdf_subject"] = st.session_state.subject
                            st.success(f"✅ Le cours de {st.session_state.subject} a été validé et diffusé avec succès!" if language == "French" else f"✅ The {st.session_state.subject} course has been successfully validated and broadcasted!")
                        else:
                            st.essror(f"🛑 Diffusion bloquée par l'IA! {response.text}" if language == "French" else f"🛑 AI bloque the broadcasting! {response.text}")
                    except Exception as e:
                        st.error("Erreur : {e}") 
            else: 
                st.warning(f"⚠️ Veuillez sélectionner unfichier PDF." if language == "French" else f"⚠️ Please select a PDF file.")
        else:
            st.title("🧠 PomoMind Social Network")
            if st.session_state["prof_pdf_name"]:
                st.info(f"🔔 **Notification Enseignant :** Un nouveau cours officiel de **{st.session_state['prof_pdf_subject']}** a été diffusé par **{st.session_state['prof_pdf_name']}**.")

            tab1, tab2 = st.tabs(["⏳ Chrono Pomodoro & Musique", "📱 Flux de cours" if language == "French" else "📱 Course Feed"])

            with tab1:
                st.subheader("📈 Session Focus Pomodoro")
                sound = st.selctbox("🎵 Ambiance sonore :", ["Silence", "Lo-Fi study", "Ondes Binaurales"] if language == "French" else ["Silence", "Lo-Fi study", "Ondes Binaurales"])
                if sound == "Lo-Fi Study":
                    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3", start_time=0)
                elif sound == "Ondes Binaurales":
                    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3", format="audio/mp3", start_time=0)

                if st.button("⏱️ Lancer ma session d'étude (10s)" if language == "French" else "Start the Session (10s)"):
                    t_box = st.empty()
                    for i in range(10, 0, -1):
                        t_box.metric(label="Reste concentré...", value=f"00:0{i}" if language == "French" else f"Stay Focused: 00:0{i}")
                        time.sleep(1)
                    st.balloons()
                    st.session_state.xp += 50
                    st.success(f"🎉 Session validée! +50 XP" if language == "French" else f"🎉 Session validated! +50 XP")
                    st.rerun()

            with tab2:
                st.subheader("📚 Flux de cours officiel." if language == "French" else "📚 Official Course Feed")
                if st.session_state["prof_pdf_name"]:
                    st.write(f"📄 **Document partagé :** {st.session_state['prof_pdf_name']}({st.session_state['prof_pdf_subject']})")
                    st.button("🖲️ Transformer le document en Flashcards" if language == "French" else "Transform the document into Flashcards")
                else:
                    st.write("Aucun document offiel n'a été partagé." if language == "French" else "No official document has been shared.")
            
