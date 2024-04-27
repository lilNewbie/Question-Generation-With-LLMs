#https://drive.google.com/file/d/1vPF_tXbH4Z7a7r-MD_Mv2AzIEXUQesG6/view?usp=sharing
#https://drive.google.com/file/d/1Cd-HCFF_VYtQaK9ugYh0G6nxXyv3K8wZ/view?usp=sharing
from lmqg import TransformersQG
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import json
import PyPDF2
import io
import gdown
import requests
from pprint import pprint
from lmqg import TransformersQG
# model = TransformersQG('lmqg/t5-base-squad-qag')
pdfs = ["https://drive.google.com/file/d/1Cd-HCFF_VYtQaK9ugYh0G6nxXyv3K8wZ/view?usp=sharing"]
op_path = 'pdfs/pdf1.pdf'

text="Cheesecake is a dessert made with a soft fresh cheese (typically cottage cheese, cream cheese, quarkv or ricotta), eggs, and sugar. It may have a crust or base made from crushed cookies (or digestive biscuits), graham crackers, pastry, or sometimes sponge cake.[1] Cheesecake may be baked or unbaked, and is usually refrigerated."
# question_answer = model.generate_qa(text)
# print(question_answer[0][0], question_answer[0][1])

def generator(pdfs, model):
    text=''
    for i in pdfs:
        r = requests.get(i)
        f = io.BytesIO(r.content)
        reader = PyPDF2.PdfReader(f)
        pages = reader.pages
        text = ' '.join([page.extract_text() for page in pages])
    question_answer = model.generate_qa(text)
    return question_answer[0][0], question_answer[0][1]

def read_pdf_from_google_drive(url):
    # Get the file ID from the Google Drive URL
    file_id = url.split('/')[-2]

    # Construct the download URL for the PDF file
    download_url = f"https://drive.google.com/uc?id={file_id}"

    # Send a GET request to download the file
    response = requests.get(download_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the PDF file locally
        with open("downloaded_file.pdf", "wb") as f:
            f.write(response.content)

        # Open the downloaded PDF file and read its contents
        with open("downloaded_file.pdf", "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            num_pages = pdf_reader.numPages
            text = ""
            for page_num in range(num_pages):
                page = pdf_reader.getPage(page_num)
                text += page.extractText()

        # Print the extracted text
        print(text)

    else:
        print("Failed to download the PDF file")

# Example usage
url = "https://drive.google.com/file/d/1Cd-HCFF_VYtQaK9ugYh0G6nxXyv3K8wZ/view?usp=sharing"
gdown.download(url, op_path, quiet=False,fuzzy=True)
# read_pdf_from_google_drive(url)