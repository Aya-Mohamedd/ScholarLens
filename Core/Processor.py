import fitz
import io
import os
import glob
from PIL import Image
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import TokenTextSplitter

def run_extraction(pdf_file):
    reader = SimpleDirectoryReader(input_files=[pdf_file])
    documents = reader.load_data()
    splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents(documents)

    output_folder = os.path.join("assets", "extracted_images")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(pdf_file)
    for page_index in range(len(doc)):
        page = doc[page_index]
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image = Image.open(io.BytesIO(base_image["image"]))
            image.save(os.path.join(output_folder, f"image_p{page_index}_{img_index}.png"))
            
    for node in nodes:
        page_label = node.metadata.get("page_label")
        if page_label:
            page_idx = int(page_label) - 1
            related_imgs = glob.glob(f"assets/extracted_images/image_p{page_idx}_*.png")
            node.metadata['image_names'] = [os.path.basename(i) for i in related_imgs] if related_imgs else "No images"
            
    return nodes