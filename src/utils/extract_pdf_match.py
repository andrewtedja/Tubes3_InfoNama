import os
import re
from typing import Optional
import PyPDF2

def extract_pdf_for_string_matching(pdf_filename: str) -> str:
    """
    Search for a PDF file across role folders and extract its content to a long string.
    
    Args:
        pdf_filename (str): PDF filename to extract

    Returns:
        str: Extracted PDF as a long string, or empty string if file not found/error
    """
    
    # Extract text
    extracted_text = extract_text_from_pdf(pdf_filename)
    
    # Process and clean text
    processed_text = _clean_text(extracted_text)
    
    return processed_text


def find_pdf_file(pdf_filename: str) -> Optional[str]:
    """
    Search for a PDF file across all role folders.
    
    Args:
        pdf_filename (str): PDF filename to extract
    
    Returns:
        Optional[str]: Full path to PDF file if found, None otherwise
    """
    
    if not os.path.exists("data"):
        print(f"Data directory 'data' does not exist")
        return None
    
    # Iterate all role folders
    for role_folder in os.listdir("data"):
        role_path = os.path.join("data", role_folder)
        
        if not os.path.isdir(role_path):
            continue
        
        # Check PDF file exists
        pdf_path = os.path.join(role_path, pdf_filename)
        if os.path.exists(pdf_path) and pdf_path.lower().endswith('.pdf'):
            return pdf_path
    
    return None


def extract_text_from_pdf(pdf_filename: str) -> str:
    """
    Extract text content from the PDF file.
    
    Args:
        pdf_path (str): Full path to the PDF file
    
    Returns:
        str: Extracted text content
    """

    # Search the PDF file
    pdf_path = find_pdf_file(pdf_filename)
    
    if not pdf_path:
        print(f"PDF file '{pdf_filename}' not found in any role folder")
        return ""
    
    print(f"Found PDF: {pdf_path}")
    
    extracted_text = ""

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
            
            if extracted_text.strip():
                print(f"Successfully extracted text ({len(pdf_reader.pages)} pages)")
                return extracted_text
    
    except Exception as e:
        print(f"PyPDF2 failed: {str(e)}")
    
    print(f"Failed to extract text from PDF: {pdf_path}")
    return ""


def _clean_text(text: str) -> str:
    """
    Clean and normalize extracted PDF text to one-line string.
    
    Args:
        text (str): Raw extracted text
    
    Returns:
        str: Cleaned one-line string
    """
    
    if not text:
        return ""
    
    # Remove over whitespaces
    text = re.sub(r'\s+', ' ', text)
    
    # Strip
    text = text.strip()
    
    return text



# Example use
if __name__ == "__main__":
    pdf_filename = "10554236.pdf"
    content = extract_pdf_for_string_matching(pdf_filename)
    
    if content:
        print(f"Extracted {len(content)} characters")
        print(f"First 500 Characters from Long String:\n{content[:500]}...")