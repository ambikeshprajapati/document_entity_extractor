# Document Entity Extractor (OCR + LLM)

A Streamlit-based application that extracts structured entities from documents (Marksheet, Offer Letter) using **OCR (PyMuPDF + Tesseract)** and **LLM (Llama3.1 via Ollama)**.  
Upload a PDF → OCR → LLM Extraction → JSON output.

---

## Features

### OCR + PDF Processing
- High-quality OCR using Tesseract
- PDF rendering via PyMuPDF
- Supports scanned PDFs

### AI-Based Entity Extraction  
Uses **Llama3.1 locally** (served using **Ollama**) to extract:

#### Marksheet:
- Name  
- Mother’s Name  
- Subject Names  
- Total Marks  

#### Offer Letter:
- Name  
- Organisation Name  
- Date  
- Designation  

### 🖥️ Streamlit UI
- Upload PDF  
- Preview first page  
- View extracted entities  
- Download JSON  

---

## 📦 Tech Stack

| Component | Technology |
|----------|------------|
| UI | Streamlit |
| OCR | Tesseract, PyMuPDF, Pytesseract |
| LLM | Llama3.1 via Ollama |
| Rendering | PyMuPDF |
| Image Handling | Pillow |
| API Client | openai-python SDK |

---

# 🛠️ Installation & Setup Guide  
Below are **all installation links** you need.

---

## 1️⃣ Clone the Repository
``bash
git clone https://github.com/your-username/document-entity-extractor.git
cd document-entity-extractor

## 2️⃣ Install Python Dependencies
pip install -r requirements.txt

## 3️⃣ Install Required External Tools
Tesseract performs the OCR on PDF images
https://github.com/UB-Mannheim/tesseract/wiki

## Ollama
ollama lets you run LLMs locally
https://ollama.com/download
