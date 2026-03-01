import sys
import os
import streamlit as st
import asyncio
from dotenv import load_dotenv

# Adding path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Core.Processor import run_extraction
from Core.Brain import process_all_nodes_in_batches
from Core.Generator import process_audio, generate_free_images_v3, create_final_video_with_subs

load_dotenv()

st.set_page_config(page_title="ScholarLens", page_icon="🔭", layout="centered")

# CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    /* File Uploader Styling */
    .stFileUploader section {
        background-color: #1a1c24;
        border: 2px dashed #2575fc;
        border-radius: 15px;
    }

    /* Primary Button Styling */
    div.stButton > button {
        width: 100%;
        border-radius: 25px;
        height: 3em;
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        font-weight: bold;
        font-size: 18px;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 20px rgba(37, 117, 252, 0.3);
    }

    /* Logo*/
    .logo-container {
        text-align: center;
        padding: 30px 0;
    }
    .logo-text {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 52px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -2px;
        margin-bottom: 0px;
    }
    .lens-part {
        color: #2575fc;
        text-shadow: 0 0 15px rgba(37, 117, 252, 0.5);
    }
    .logo-sub {
        color: #888;
        font-size: 12px;
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-top: -10px;
    }
    </style>
    """, unsafe_allow_html=True) 

# Logo
st.markdown("""
    <div class="logo-container">
        <div class="logo-text">SCHOLAR<span class="lens-part">LENS</span></div>
        <div class="logo-sub">From Theory to Vision</div>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠️ Lab Settings")
    with st.expander("Secrets & Tokens"):
        google_key = st.text_input("Gemini API Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password")
        hf_token = st.text_input("HuggingFace Token", value=os.getenv("HF_TOKEN", ""), type="password")
    
    st.divider()
    st.caption("Powered by Gemini 1.5 & Flux ⚡")

# --- Main Work Interface ---
uploaded_file = st.file_uploader("", type="pdf")

if not uploaded_file:
    st.markdown("<p style='text-align: center; color: #666;'>Drop your research PDF here to start the cinematic transformation.</p>", unsafe_allow_html=True)

if uploaded_file and google_key:
    if st.button("Unleash the Vision 🎬"):
        os.environ["GOOGLE_API_KEY"] = google_key
        os.environ["HF_TOKEN"] = hf_token
        
        pdf_path = uploaded_file.name
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.status("🏗️ Building your Masterpiece...", expanded=True) as status:
            st.write("📖 **Reading** | Extracting core insights from PDF...")
            nodes = run_extraction(pdf_path)
            
            st.write("🎬 **Scripting** | Gemini is crafting the narrative...")
            script = process_all_nodes_in_batches(nodes)
            
            st.write("🔊 **Voicing** | Synthesizing professional narration...")
            asyncio.run(process_audio('final_full_research_script.json'))
            
            st.write("🎨 **Visualizing** | Flux is painting the scenes...")
            generate_free_images_v3('final_full_research_script.json')
            
            st.write("🎥 **Assembling** | Rendering final video layers with FFmpeg...")
            create_final_video_with_subs()
            
            status.update(label="✨ Production Complete!", state="complete")

        # --- Updated Video Display Logic ---
        # The filename must match the FINAL_VIDEO_NAME in Generator.py
        final_output_file = "ScholarLens_Final_Subtitled.mp4"

        if os.path.exists(final_output_file):
            st.success("Your video is ready!")
            st.video(final_output_file)
            with open(final_output_file, "rb") as file:
                st.download_button(
                    label="📥 Download Masterpiece", 
                    data=file, 
                    file_name="ScholarLens_Video.mp4",
                    mime="video/mp4"
                )