import hashlib, time, streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="PomoMind AI", page_icon="🔒")

# --- INITIALISATION STATE ---
for key, val in [("logged_in", False), ("role", "Student"), ("username", ""), ("subject", None), ("xp", 150), ("prof_pdf_name", None), ("prof_pdf_subject", None), ("dernier_clic_prof", 0.0)]:
    if key not in st.session_state: st.session_state[key] = val

language = st.sidebar.selectbox("Select Language / Choisir Langue", ["English", "French"])
FR = language == "French"

# --- ÉCRAN DE CONNEXION ---
if not st.session_state["logged_in"]:
    st.title("🔒 PomoMind AI - Portail" if FR else "🔒 PomoMind AI - Portal")

    st.subheader("Veuillez choisir votre profil pour accéder à votre espace sécurisé." if FR else "Please choose your profile to access your secure space.")
    role_choice = st.radio("🔑 Choisis ton profil :" if FR else "🔑 Select your role :", ["Student", "Professor"] if not FR else ["Elève", "Professeur"])
    username_input = st.text_input("Identifiant / Email" if FR else "Username / Email", placeholder="student, prof_bio, prof_cyber")
    password_input = st.text_input("Mot de Passe" if FR else "Password", type="password")

    if st.button("Se connecter" if FR else "Login"):
        users = {
            "student": {"pass": "student123", "role": "Student", "sub": None},
            "prof_bio": {"pass": "prof_bio123", "role": "Professor", "sub": "Biologie"},
            "prof_cyber": {"pass": "prof_cyber123", "role": "Professor", "sub": "Cybersecurity"}
        }
        hashed = hashlib.sha256(password_input.encode()).hexdigest()
        if username_input in users and hashed == hashlib.sha256(users[username_input]["pass"].encode()).hexdigest() and role_choice == users[username_input]["role"]:
            st.session_state.update({"logged_in": True, "role": users[username_input]["role"], "username": username_input, "subject": users[username_input]["sub"]})
            st.success("🔒 Bienvenue !" if FR else "🔒 Welcome !")
            st.rerun()
        else:
            st.error("❌ Identifiant, mot de passe ou rôle incorrect." if FR else "❌ Invalid username, password or role.")

# --- ESPACE CONNECTÉ ---
else:
    st.sidebar.title(f"👤 Espace {st.session_state.role}" if FR else f"👤 {st.session_state.role} Area")
    if st.session_state.role == "Student":
        st.sidebar.metric("🔥 Série d'étude" if FR else "🔥 Study Streak", "3 Jours" if FR else "3 days")
        st.sidebar.metric("✨ Score global" if FR else "✨ Global Score", f"{st.session_state.xp} XP")

    demo_mode = st.sidebar.checkbox("⚙️ Mode Démo (Sans clé API)" if FR else "⚙️ Demo Mode (No API Key)", value=False)
    api_key_input = "DEMO" if demo_mode else st.sidebar.text_input("Clé API Gemini:" if FR else "Gemini API Key:", type="password")

    if st.sidebar.button("🚪 Déconnexion" if FR else "🚪 Logout"):
        st.session_state.clear(); st.rerun()

    # --- INTERFACE PROFESSEUR ---
    if st.session_state.role == "Professor":
        st.title(f"👨‍🏫 Tableau de Bord Enseignant - Spécialité: {st.session_state.subject}" if FR else f"👨‍🏫 Teacher Dashboard - Specialty: {st.session_state.subject}")
        st.write("Envoyez vos supports de cours officiels à la classe." if FR else "Send your official course materials to the class.")
        
        uploaded_pdf = st.file_uploader("Glissez et déposez le cours officiel (Format PDF) :" if FR else "Drag and drop your official course material (PDF):", type=["pdf"])
        
        if st.button("🖲️ Diffusez le cours de la classe" if FR else "🖲️ Broadcast the class course"):
            temps_actuel = time.time()
            if temps_actuel - st.session_state["dernier_clic_prof"] < 10:
                st.warning("⚠️ Anti-Spam: Veuillez attendre 10 secondes." if FR else "⚠️ Anti-Spam: Please wait 10 seconds.")
            elif not api_key_input:
                st.error("⚠️ Veuillez configurer votre clé API Gemini à gauche." if FR else "⚠️ Please set up your Gemini API key on the left.")
            elif uploaded_pdf is None:
                st.warning("⚠️ Veuillez sélectionner un fichier PDF." if FR else "⚠️ Please select a PDF file.")
            else:
                with st.spinner("L'agent IA vérifie le cours..." if FR else "The AI agent is verifying the course..."):
                    try:
                        if demo_mode:
                            time.sleep(1); ai_text = "[VALIDE]"
                        else:
                            client = genai.Client(api_key=api_key_input, http_options=types.HttpOptions(api_version="v1"))
                            pdf_part = types.Part.from_bytes(data=uploaded_pdf.read(), mime_type="application/pdf")
                            prompt = f"Tu es l'agent de sécurité de PomoMind AI. Rôle: Vérifier que le document correspond à : {st.session_state.subject}. Réponds UNIQUEMENT par [VALIDE] ou [INVALIDE: Raison]"
                            try:
                                ai_text = client.models.generate_content(model="gemini-3.8-flash", contents=[prompt, pdf_part]).text
                            except Exception as err:
                                if "503" in str(err) or "UNAVAILABLE" in str(err):
                                    ai_text = client.models.generate_content(model="gemini-2.5-pro", contents=[prompt, pdf_part]).text
                                else: raise err
                        
                        if "[VALIDE]" in ai_text:
                            st.session_state.update({"dernier_clic_prof": temps_actuel, "prof_pdf_name": uploaded_pdf.name, "prof_pdf_subject": st.session_state.subject})
                            st.success(f"✅ Le cours de {st.session_state.subject} a été diffusé avec succès!" if FR else f"✅ The {st.session_state.subject} course has been successfully broadcasted!")
                        else:
                            st.error(f"🛑 Diffusion bloquée par l'IA! {ai_text}" if FR else f"🛑 AI blocked the broadcasting! {ai_text}")
                    except Exception as e: st.error(f"Erreur : {e}")

    # --- INTERFACE ÉTUDIANT (RÉSEAU SOCIAL) ---
    elif st.session_state.role == "Student":
        st.title("🧠 PomoMind Social Network")
        if st.session_state["prof_pdf_name"]:
            st.info(f"🔔 **Notification Enseignant :** Un nouveau cours officiel de **{st.session_state['prof_pdf_subject']}** a été diffusé par *'{st.session_state['prof_pdf_name']}'*" if FR else f"🔔 **Teacher Notification:** A new official course of **{st.session_state['prof_pdf_subject']}** has been broadcasted by *'{st.session_state['prof_pdf_name']}'*")
        
        tab1, tab2 = st.tabs(["⏳ Chrono Pomodoro & Musique", "📱 Flux de cours" if FR else "📱 Course Feed"])
        
        with tab1:
            st.subheader("📈 Session Focus Pomodoro")
            sound = st.selectbox("🎵 Ambiance sonore :" if FR else "🎵 Sound atmosphere :", ["Silence", "Lo-Fi study", "Ondes Binaurales" if FR else "Binaural Waves"])
            if sound in ["Lo-Fi study", "Ondes Binaurales", "Binaural Waves"]:
                url_sound = "https://soundhelix.com" if sound == "Lo-Fi study" else "https://soundhelix.com"
                st.audio(url_sound, format="audio/mp3", start_time=0)

            if st.button("⏱️ Lancer ma session d'étude (10s)" if FR else "⏱️ Start the Session (10s)"):
                t = st.empty()
                for i in range(10, 0, -1):
                    t.metric("Reste concentré..." if FR else "Stay focused...", f"00:0{i}"); time.sleep(1)
                st.balloons(); st.session_state.xp += 50; st.success("🎉 Session validée! +50 XP" if FR else "🎉 Session validated! +50 XP"); st.rerun()
                
        with tab2:
            st.subheader("📚 Flux de cours officiel." if language == "French" else "📚 Official Course Feed")
            if st.session_state["prof_pdf_name"] is not None:
                st.write(f"📄 **Document partagé :** {st.session_state['prof_pdf_name']} ({st.session_state['prof_pdf_subject']})")
                
                # Le bouton IA s'active !
                if st.button("🖲️ Transformer le document en Flashcards" if language == "French" else "Transform the document into Flashcards"):
                    if not api_key_input:
                        st.error("⚠️ Veuillez configurer votre clé API Gemini à gauche pour activer le cerveau de l'IA." if language == "French" else "⚠️ Please set up your Gemini API key on the left to enable the AI.")
                    else:
                        with st.spinner("L'agent IA PomoMind découpe ton cours en Flashcards TikTok..." if language == "French" else "The AI agent is slicing your course into TikTok Flashcards..."):
                            try:
                                # Connexion au client Gemini avec la clé fournie à gauche
                                client = genai.Client(api_key=api_key_input)
                                
                                # Consignes strictes pour formater le résumé addictif
                                prompt_flashcards = f"""
                                Tu es l'Agent Rétention de PomoMind AI. Ton rôle est de transformer le cours officiel fourni par le professeur en un feed captivant comme sur TikTok (Méthode Feynman).
                                Génère exactement 3 Flashcards courtes et percutantes.
                                Chaque Flashcard doit obligatoirement contenir :
                                1. Un titre accrocheur avec émojis.
                                2. Une explication scientifique résumée avec des mots ultra-simples.
                                3. Une analogie ou un exemple amusant basé sur la vie quotidienne locale au Cameroun (ex: le marché, les beignets-haricots, le taxi de Yaoundé).
                                """
                                
                                # Puisqu'on utilise les données en mémoire, on demande à Gemini de traiter la demande textuelle basée sur le sujet diffusé
                                response = client.models.generate_content(
                                    model="gemini-2.5-flash",
                                    contents=f"{prompt_flashcards}\n\nSujet du cours à résumer : {st.session_state['prof_pdf_subject']} - Nom du fichier : {st.session_state['prof_pdf_name']}"
                                )
                                
                                st.markdown("---")
                                st.success("📱 Flashcards générées avec succès ! +20 XP" if language == "French" else "📱 Flashcards successfully generated! +20 XP")
                                st.session_state.xp += 20
                                st.write(response.text)
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Erreur IA : {e}")
            else:
                st.write("Aucun document officiel n'a été partagé." if language == "French" else "No official document has been shared.")
   