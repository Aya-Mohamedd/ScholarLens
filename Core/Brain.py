import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

def generate_script_from_nodes(nodes_with_images, start_id=1, max_scenes=15):
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    context_text = ""
    for node in nodes_with_images:
        context_text += f"Content: {node.get_content()}\nImages: {node.metadata.get('image_names')}\n---\n"

    # الـ Prompt بتاعك حرفياً (تم اختصاره هنا للعرض، ضعي نسختك الكاملة)
    prompt = f"You are an expert Educational Content Creator... Context: {context_text} OUTPUT FORMAT: Strict JSON list."
    
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    cleaned_text = response.text.strip()
    if cleaned_text.startswith("```json"): cleaned_text = cleaned_text[7:-3].strip()
    return json.loads(cleaned_text)

def process_all_nodes_in_batches(all_nodes, batch_size=15, filename='final_full_research_script.json'):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    
    # معالجة أول 15 نود كما في كودك الأصلي
    batch_script = generate_script_from_nodes(all_nodes[:batch_size])
    if batch_script:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(batch_script, f, indent=2, ensure_ascii=False)
    return batch_script