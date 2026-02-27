import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from gtts import gTTS
from io import BytesIO
import os
from dotenv import load_dotenv
from docx import Document

# ================== LOAD ENV ==================
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# ================== PAGE CONFIG ==================
st.set_page_config(page_title="TransLingua Pro", layout="centered")

# ================== DEMO MODE ==================
demo_mode = False
if not api_key or api_key == "gsk_your_actual_api_key_here":
    demo_mode = True
    st.sidebar.warning("🚀 Demo Mode Active - Add GROQ API key for real translations")

# ================== LANGUAGE OPTIONS ==================
language_codes = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Italian": "it",
    "Portuguese": "pt",
    "Arabic": "ar",
    "Japanese": "ja"
}

languages = list(language_codes.keys())

# ================== LANGUAGE SELECT ==================
st.title("🌍 Choose Your Languages")

source_language = st.selectbox("Select Source Language", languages)
target_language = st.selectbox("Select Target Language", languages)

if source_language == target_language:
    st.warning("⚠️ Please choose different languages.")

# ================== PROMPT ==================
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a professional translator. "
         "Translate from {source_language} to {target_language}. "
         "Return ONLY the translated text."),
        ("user", "{text}")
    ]
)

# ================== TRANSLATION FUNCTION ==================
def real_translate(text):
    groq = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        temperature=0
    )

    chain = prompt | groq | StrOutputParser()

    return chain.invoke({
        "source_language": source_language,
        "target_language": target_language,
        "text": text
    })

# ================== SIDEBAR MENU ==================
st.sidebar.image("logo1.png", use_container_width=True)
st.sidebar.markdown("---")
menu = st.sidebar.radio("Choose Option", [
    "Text Translation",
    "File Translation"
])

# =====================================================
# 1️⃣ TEXT TRANSLATION
# =====================================================
if menu == "Text Translation":

    st.header("📝 Real-Time Text Translation")

    text_input = st.text_input("Enter text to translate")

    if text_input and source_language != target_language:

        try:
            if demo_mode:
                translation = f"[DEMO] {text_input} → (Translated to {target_language})"
            else:
                translation = real_translate(text_input)

            st.success("Translation:")
            st.markdown(f"**{translation}**")

            if st.button("🔊 Play Audio"):
                tts = gTTS(text=translation, lang=language_codes[target_language])
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                st.audio(audio_buffer.read(), format="audio/mp3")

        except Exception as e:
            st.error(f"Translation failed: {str(e)}")

# =====================================================
# 2️⃣ FILE TRANSLATION
# =====================================================
elif menu == "File Translation":

    st.header("📄 File Upload & Translation")

    uploaded_file = st.file_uploader("Upload .txt or .docx file", type=["txt", "docx"])

    if uploaded_file:

        if uploaded_file.name.endswith(".txt"):
            content = uploaded_file.read().decode("utf-8")
        else:
            doc = Document(uploaded_file)
            content = "\n".join([para.text for para in doc.paragraphs])

        st.text_area("File Content", content, height=200)

        if st.button("Translate File") and source_language != target_language:

            try:
                if demo_mode:
                    translation = f"[DEMO] File translated to {target_language}"
                else:
                    translation = real_translate(content)

                st.success("Translated Content:")
                st.markdown(f"**{translation}**")

            except Exception as e:
                st.error(f"File translation failed: {str(e)}")