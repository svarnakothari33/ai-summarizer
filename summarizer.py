import requests
import json
import argparse
import os
from PyPDF2 import PdfReader
import docx

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF file: {e}")
    return text

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX file: {e}")
    return text

def extract_text_from_file(file_path):
    """Extract text based on file type."""
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_extension == ".docx":
        return extract_text_from_docx(file_path)
    elif file_extension == ".txt":
        with open(file_path, 'r') as file:
            return file.read()
    else:
        print(f"Unsupported file type: {file_extension}")
        return None

def send_prompt(content):
    url = "http://127.0.0.1:11434/api/chat"

    data = {
        "model": "llama3.2:latest",
        "messages": [
            {
                "role": "user",
                "content": f"Summarize the following text : {content}"
            },
        ],
        "stream": True
    }

    response = requests.post(url, json=data, stream=True)
    print(response.status_code)
    if response.status_code == 200:
        full_response = ''
        for line in response.iter_lines():
            if line:
                try:
                    json_object = json.loads(line)
                    if 'message' in json_object and 'content' in json_object['message']:
                        chunk = json_object['message']['content']
                        full_response += chunk
                except json.JSONDecodeError:
                    pass
        print()
        return full_response
    else:
        print(f"Error: {response.status_code}")
        return response.text

def main():
    parser = argparse.ArgumentParser(description="Summarize text or document content.")
    parser.add_argument('-t', '--textfile', type=str, help="Path to the text, PDF, or DOCX file to summarize.")
    parser.add_argument('-s', '--string', type=str, help="Text string to summarize.")

    args = parser.parse_args()

    if args.textfile:
        # Extract content from file
        content = extract_text_from_file(args.textfile)
        if content is None:
            return
    elif args.string:
        content = args.string
    else:
        print("Error: You must provide either a text file (-t) or a text string (-s).")
        return

    summary = send_prompt(content)
    print("Summary:")
    print(summary)

if __name__ == "__main__":
    main()
