import streamlit as st
import time
from services.translation_service import translate_text

def render_translation_workshop(project):
    st.title("🌐 Translate Content")
    st.subheader(f"Project: {project['name']}")
    
    if st.session_state.translation_mode == "basic":
        st.info("✨ Basic Mode: Fast, straightforward translation")
        st.markdown(f"**From:** {project.get('source_lang', 'Auto')} → **To:** {project.get('target_lang', 'Select language')}")
    else:
        with st.expander("⚙️ Current Settings", expanded=True):
            st.json(project.get("metadata", {}))
            st.write(f"**Mode:** {st.session_state.translation_mode.capitalize()}")
            
            if project.get("user_feedback"):
                st.markdown("### 📝 Active Feedback")
                feedback = project["user_feedback"]
                if feedback.get("issues"):
                    st.write("**Improvements requested:**")
                    for issue in feedback["issues"]:
                        st.write(f"- {issue}")
                if feedback.get("custom"):
                    st.write("**Specific instructions:**")
                    st.write(feedback["custom"])
        
        if st.session_state.translation_mode == "agentic":
            st.markdown("### 🤖 Agentic Configuration")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Framework:** {st.session_state.get('framework', 'State Machine (LangGraph)')}")
            with col2:
                st.write(f"**Intensity:** {st.session_state.get('intensity', 3)}/4")
    
    st.markdown("### ✍️ Source Content")
    
    # Always use the last source text if in retranslate mode
    if st.session_state.get("retranslate_mode", False):
        source_text = st.session_state.get("last_source_text", "")
        st.info("♻️ Retranslating with feedback")
        st.text_area("Original text:", 
                   value=source_text, 
                   height=250, 
                   key="original_text",
                   disabled=True)
    else:
        source_text = st.text_area("Enter text to translate:", 
                                 height=250, 
                                 placeholder="Type or paste content here...", 
                                 key="source_text")
    
    if not st.session_state.get("retranslate_mode", False) and source_text:
        st.session_state.last_source_text = source_text
    
    if st.session_state.translation_mode == "basic":
        source_lang = project.get("source_lang", "Auto")
        target_lang = project.get("target_lang", "English")
    else:
        col1, col2 = st.columns(2)
        with col1:
            source_lang = st.selectbox("From Language:", 
                                      ["Auto", "English", "Hindi", "Tamil", "Russian", "French"])
        with col2:
            target_lang = st.selectbox("To Language:", 
                                      ["Tamil", "Hindi", "English", "Russian", "French"])
    
    if st.button("✨ Translate", disabled=not source_text):
        with st.status("🚀 Translating...", expanded=True) as status:
            if st.session_state.translation_mode == "basic":
                st.write("⚡ Fast translation using Gemini...")
                time.sleep(1)
            elif st.session_state.translation_mode == "advanced":
                st.write("🧠 Processing with advanced AI...")
                time.sleep(1)
            else:
                framework = st.session_state.get("framework", "State Machine (LangGraph)")
                if "LangGraph" in framework:
                    steps = ["Initializing translation workflow", "Analyzing context", "Translating"]
                    if st.session_state.intensity >= 3: 
                        steps.append("Cultural adaptation")
                    if st.session_state.intensity >= 4: 
                        steps.append("Quality validation")
                    
                    for step in steps:
                        st.write(f"🔹 {step}...")
                        time.sleep(0.5)
                else:
                    steps = ["Translator processing text"]
                    if st.session_state.intensity >= 2:
                        steps.append("Reviewer validating quality")
                    if st.session_state.intensity >= 3: 
                        steps.append("Cultural expert adapting content")
                    
                    for step in steps:
                        st.write(f"🔹 {step}...")
                        time.sleep(0.5)
            
            translation_result = translate_text(
                source_text,
                source_lang,
                target_lang,
                project.get("metadata", {}),
                st.session_state.translation_mode,
                st.session_state.get("framework"),
                st.session_state.get("intensity", 3),
                project.get("user_feedback", {})
            )
            
            version = len(project.get("history", [])) + 1
            new_entry = {
                "text": source_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "translation": translation_result['translation'],
                "version": version,
                "mode": st.session_state.translation_mode,
                "framework": st.session_state.get("framework"),
                "intensity": st.session_state.get("intensity", 3),
                "context": translation_result.get('context'),
                "metadata": translation_result.get('metadata', {})
            }
            
            if "history" not in project:
                project["history"] = []
            
            project["history"].append(new_entry)
            st.session_state.project = project
            st.session_state.retranslate_mode = False
            
            status.update(label="✅ Translation Complete!", state="complete")
            st.session_state.current_step = "results"
            st.rerun()
    
    if st.button("← Back to Settings"):
        st.session_state.current_step = "metadata_setup"
        st.rerun()