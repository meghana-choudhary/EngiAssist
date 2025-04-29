from unstructured.partition.pdf import partition_pdf
import base64
from PIL import Image
import pandas as pd
from groq import Groq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')


PDF_FOLDER = "docs"
TEXT_FOLDER = "Texts"
IMAGE_FOLDER = "Images"
IMAGE_SUMMERY = "Image_Summary"
CSV_FILE = "Final_Embeddings.csv"

e_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_text_senttrf_embedding(text: str):
    result = e_model.encode(text)
    return result

def extract_and_save_data(pdf_file, text_folder, image_folder):
    """
    Extracts text, images, and tables from a PDF file and saves them to specified folders.

    Args:
        pdf_file (str): Path to the PDF file.
        text_folder (str): Path to the folder where text files will be saved.
        image_folder (str): Path to the folder where images will be saved.
    """

    # Create folders if they don't exist
    os.makedirs(text_folder, exist_ok=True)
    os.makedirs(image_folder, exist_ok=True)


    # Get PDF name without extension
    pdf_name = os.path.splitext(os.path.basename(pdf_file))[0]

    # Partition the PDF
    elements = partition_pdf(
        filename=pdf_file,
        extract_images_in_pdf=True,
        infer_table_structure= False,
        strategy= 'hi_res'
    )

    #Extract and save text
    pages = {}
    for element in elements:
        if element.category == "NarrativeText":
            if element.metadata.page_number in pages:
                pages[element.metadata.page_number] += "\n"+element.text
            else:
                pages[element.metadata.page_number] = element.text
    for page_number, page_text in pages.items():
        if page_text:
            text_file_name = f"{pdf_name}_Page_{page_number}.txt"
            text_file_path = os.path.join(text_folder, text_file_name)
            with open(text_file_path, "w") as f:
                f.write(page_text)

    # Extract and save images
    image_id = 1
    for element in elements:
        if element.metadata and element.metadata.image_path:
            image = Image.open(element.metadata.image_path)
            image_file_name = f"{pdf_name}_Page_{element.metadata.page_number}_id_{image_id}.png"
            image_file_path = os.path.join(image_folder, image_file_name)
            image.save(image_file_path)
            image_id += 1

def generate_image_descriptions_and_save(image_folder: str, output_folder: str):
    """
    Generates descriptions of images using Llama 11b vision model via Groq and saves them.

    Args:
        image_folder (str): Path to the folder containing images.
        output_folder (str): Path to the folder where descriptions will be saved.
    """

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Initialize Groq client
    client = Groq(api_key=GROQ_API_KEY)

    # Iterate through images and generate descriptions
    for img_file in tqdm(sorted(os.listdir(image_folder))):
        img_path = os.path.join(image_folder, img_file)

        if img_file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            # Encode image to Base64
            with open(img_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            # Call Llama 11b vision model using Groq
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Summarize this image."},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                )

                # Extract and save the description
                description = chat_completion.choices[0].message.content
                output_file_name = os.path.splitext(img_file)[0] + ".txt"
                output_file_path = os.path.join(output_folder, output_file_name)

                with open(output_file_path, "w") as f:
                    f.write(description)

            except Exception as e:
                print(f"Error processing {img_file}: {e}")

    print("Image descriptions generated and saved successfully!")

def generate_embeddings(text_folder, image_folder):

    genre_mapping = {
        "Web": "Web and Internet Technology",
        "BA": "Business Analytics and Entrepreneurship",
        "PEPM": "Professional Ethics and Project Management",
        "Ecomm": "Ecommerce"
    }


    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, chunk_overlap=128, separators=["\n\n", "\n", " ", ""]
    )
    df = pd.DataFrame(
        [], columns=["File", "Page", "Chunk", "Chunk_Text", "Type", "Genre", "Vectors"]
    )
    genre = ""
    # # Generate embeddings for texts
    for text_file in tqdm(os.listdir(text_folder)):
        for key in genre_mapping.keys():
            if key in text_file:
                genre = genre_mapping.get(key)
        with open(os.path.join(text_folder, text_file), "r", encoding="utf-8") as f:
            # Check if the file name contains "_page_"
            if "_Page_" in text_file:
                file_name = text_file.split("_Page_")[0]
                page_number = text_file.split("_Page_")[1].split(".")[0]
            else:  # If not, assume it's a single-page file
                file_name = text_file.rsplit(".", 1)[0]
                page_number = "1"  # Or any default value for single-page files

            content = f.read()
            chunks = splitter.split_text(content)
            for i, chunk in enumerate(chunks):
                em = generate_text_senttrf_embedding(chunk)
                df.loc[len(df)] = [file_name, page_number, i, chunk, "Text", genre, em]

    # Generate image embeddings
    for image_file in tqdm(os.listdir(image_folder)):
        for key in genre_mapping.keys():
            if key in text_file: # Change this to image_file
                genre = genre_mapping.get(key)
        with open(os.path.join(image_folder, image_file), "r", encoding="utf-8") as f:
            content = f.read()
            em = generate_text_senttrf_embedding(content).ravel()
            # Check if the image file contains "_Page_" before splitting
            if "_Page_" in image_file:
                file_name = image_file.split("_Page_")[0].split(".")[0]
                page_number = image_file.split("_Page_")[1].split("_id_")[0]
                img_number = image_file.split("_Page_")[1].split("_id_")[1].split(".")[0]
            else:
                # Handle cases where the image file doesn't contain "_Page_"
                file_name = image_file.rsplit(".", 1)[0]  # Or extract filename differently
                page_number = "1"  # Or assign a default page number
                img_number = "1" # Or assign a default image number

            df.loc[len(df)] = [
                file_name,
                page_number,
                img_number,
                content,
                "Image",
                genre,
                em
            ]

    if os.path.exists(CSV_FILE):
        edf = pd.read_csv(CSV_FILE)
        df = pd.concat([edf, df])


    df.to_csv(CSV_FILE, index=False)
    print("Embeddings Generated")

for file in tqdm(os.listdir(PDF_FOLDER)):
  if file.endswith(".pdf"):
    extract_and_save_data(os.path.join(PDF_FOLDER, file), TEXT_FOLDER, IMAGE_FOLDER)

generate_image_descriptions_and_save("Images", "Image_Summary")

generate_embeddings("Texts",IMAGE_SUMMERY)
