import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import json
from openai import OpenAI
import tempfile
import os

# Configure Tesseract (Windows only - you might want to make this configurable)
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except:
    st.warning("Tesseract not found at default location. Please configure the path.")

# Initialize OpenAI client
client = OpenAI(base_url="http://localhost:11434/v1", api_key="none")

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using OCR"""
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Render page to a high-resolution PNG
        pix = page.get_pixmap(dpi=200)
        img_data = pix.tobytes("png")
        
        # Load image into Pillow
        image = Image.open(io.BytesIO(img_data))
        
        # OCR using pytesseract
        text = pytesseract.image_to_string(image, lang="eng")
        full_text += f"\n\n--- Page {page_num + 1} ---\n{text}"
    
    doc.close()
    print("OCR Done")
    return full_text

def extract_entities_with_llm(raw_text, document_type):
    """Extract entities using LLM based on document type"""
    
    # Define entities based on document type
    if document_type == "marksheet":
        entities = ["Name", "Mothers Name", "Subject Names", "Total Marks"]
    else:  # offer letter
        entities = ["Name", "Organisation Name", "Date", "Designation"]
    
    SYSTEM_PROMPT = "You are an AI Assistant that extracts structured information from given documents"
    
    prompt = f"""
    Extract the following entities from the given text:

    Entities: {entities}
    Text: {raw_text}

    Instructions:
    1. Read the full text and extract the most relevant value for each entity.
    2. The output MUST be a valid JSON object.
    3. The JSON MUST contain ONLY the entities as keys and their extracted values as strings.
    4. If an entity is not found in the text, set its value to null.
    5. The final answer MUST be only the JSON object and nothing else.
    6. Do NOT add explanations, comments, extra fields, or text outside the JSON.
    7. Do NOT give any notes.
    8. Do NOT mention any extra characters in the result.
    9. Date should always be in "MM-DD-YYYY" format.

    """
    print("calling LLM")
    try:
        response = client.chat.completions.create(
            model="llama3.1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300,
        )
        
        output = response.choices[0].message.content
        
        # Try to parse the JSON response
        try:
            entities_dict = json.loads(output)
            return entities_dict
        except json.JSONDecodeError:
            st.error("Failed to parse LLM response as JSON")
            return {}
            
    except Exception as e:
        st.error(f"Error calling LLM: {e}")
        return {}

def main():
    st.set_page_config(page_title="Document Entity Extractor", layout="wide")
    
    st.title("Document Entity Extractor")
    st.markdown("Upload a PDF document and extract key entities automatically")
    
    # Initialize session state
    if 'extracted_entities' not in st.session_state:
        st.session_state.extracted_entities = None
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    
    # Sidebar for upload and settings
    with st.sidebar:
        st.header("Upload Document")
        
        # Document type selection
        document_type = st.selectbox(
            "Select Document Type:",
            ["marksheet", "offer letter"],
            help="Choose the type of document to extract appropriate entities"
        )
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF document to extract entities from"
        )
        
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            
            # Process button
            if st.button("Extract Entities", type="primary"):
                with st.spinner("Processing document..."):
                    # Save uploaded file to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    try:
                        # Extract text from PDF
                        raw_text = extract_text_from_pdf(tmp_file_path)
                        
                        # Extract entities using LLM
                        st.session_state.extracted_entities = extract_entities_with_llm(raw_text, document_type)
                        
                    except Exception as e:
                        st.error(f"Error processing document: {e}")
                    finally:
                        # Clean up temporary file
                        os.unlink(tmp_file_path)
    
    # Main content area
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Document Preview")
        
        if st.session_state.uploaded_file is not None:
            # Display PDF
            st.write(f"**Uploaded File:** {st.session_state.uploaded_file.name}")
            
            # Show PDF preview (first page as image)
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(st.session_state.uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                doc = fitz.open(tmp_file_path)
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=150)
                img_data = pix.tobytes("png")
                doc.close()
                
                st.image(img_data, caption="First Page Preview", width="stretch")
                
                # Clean up
                os.unlink(tmp_file_path)
                
            except Exception as e:
                st.error(f"Error displaying PDF preview: {e}")
        else:
            st.info("Please upload a PDF file to see preview")
    
    with col2:
        st.header("Extracted Entities")
        
        if st.session_state.extracted_entities:
            # Define entity labels based on document type
            if document_type == "marksheet":
                entity_labels = {
                    "Name": "Student Name",
                    "Mothers Name": "Mother's Name", 
                    "Subject Names": "Subjects",
                    "Total Marks": "Total Marks"
                }
            else:  # offer letter
                entity_labels = {
                    "Name": "Candidate Name",
                    "Organisation Name": "Organization",
                    "Date": "Date", 
                    "Designation": "Designation"
                }
            
            # Display entities in a nice format
            for entity_key, entity_value in st.session_state.extracted_entities.items():
                if entity_key in entity_labels:
                    label = entity_labels[entity_key]
                    
                    st.markdown(f"""
                    <div style="padding: 10px; border-left: 4px solid #4CAF50; background-color: #f9f9f9; margin: 10px 0;">
                        <strong>{label}</strong><br>
                        <span style="color: #333; font-size: 16px;">{entity_value if entity_value else 'Not found'}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Download button for extracted data
            json_data = json.dumps(st.session_state.extracted_entities, indent=2)
            st.download_button(
                label="Download Extracted Data (JSON)",
                data=json_data,
                file_name=f"extracted_entities_{document_type}.json",
                mime="application/json"
            )
            
        else:
            if st.session_state.uploaded_file and not st.session_state.extracted_entities:
                st.info("Click 'Extract Entities' to process the document")
            else:
                st.info("Upload a PDF and select document type to extract entities")

if __name__ == "__main__":
    main()