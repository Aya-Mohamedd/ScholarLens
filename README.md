# 📝 Research-to-Video Generator (ScholarLens)

An automated pipeline designed to transform academic PDF research papers into engaging, professional educational videos. This project leverages **Generative AI** and **Local GPU Inference** to create visual assets, synthesize voiceovers, and sync subtitles.

---

## 🚀 Key Features

* **PDF Intelligence:** Automatically extracts text and identifies key visual data (charts/tables).
* **AI Scripting:** Transforms dense academic language into a structured 50-scene video script.
* **Hybrid Visual Generation:** Integrates **real figures** from the research paper.
* Generates **Minimalist 2D Vector Art** using **SDXL-Turbo** for abstract concepts.


* **Dynamic Subtitling:** Hardcoded professional subtitles synced with the narration.
* **High Performance:** Optimized for Google Colab T4 GPU with zero-latency local generation.

---

## 🛠️ Tech Stack

| Component | Technology |
| --- | --- |
| **Language Model** | Gemini 2.5 Flash (Scripting & Analysis) |
| **Image Generation** | SDXL-Turbo (Stability AI) |
| **PDF Processing** | PyMuPDF (fitz) |
| **Audio/Video** | gTTS / FFmpeg |
| **Environment** | Python 3.12 / Google Colab |

---

## 📖 How It Works

### 1. Analysis & Extraction

The system parses the PDF and uses **Gemini** to categorize content into scenes. It differentiates between scenes that require a real figure from the paper and those that need an AI-generated icon.

### 2. Fast Visual Generation

To avoid server errors (like the infamous HTTP 530), the project uses a **Local Inference Pipeline**.

* **Model:** `sdxl-turbo`
* **Inference:** 1-Step Euler Ancestral sampling.
* **Style:** Minimalist, academic blue/teal palette, white background for maximum subtitle clarity.

### 3. Video Assembly

Using `FFmpeg`, the system merges:

* Generated/Extracted PNG images.
* Generated MP3 narration.
* Timed SRT Subtitles.

---

## 💻 Installation & Usage

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ScholarLens.git

# 2. Install dependencies
pip install diffusers transformers accelerate gTTS SpeechRecognition

# 3. Run the generator
python main.py --input research_paper.pdf

```

---

## 🛠️ Memory Optimization (Crucial for T4 GPU)

During development, we implemented several memory-saving techniques to handle high-resolution generation on limited hardware:

* `pipe.enable_model_cpu_offload()`: To manage VRAM efficiently.
* `torch.inference_mode()`: To reduce overhead during generation.
* `AutoPipelineForText2Image`: For fast weight loading.

---

## 🌟 Future Improvements

* [ ] Integration with **Imagen 3** via Google Vertex AI for higher semantic accuracy.
* [ ] 3D Cinematic camera movements for images.
* [ ] Multi-language support for research translation.

---

## 🤝 Acknowledgments

* **Stability AI** for the SDXL-Turbo weights.
* **Google AI** for the Gemini 3 Flash API.
