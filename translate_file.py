import argparse
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import PyPDF2
import docx

def translate_content(client, content, dest_lang, model):
    PROMPT = os.getenv("PROMPT")
    prompt= PROMPT.format(content=content, dest_lang=dest_lang)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def process_pdf(pdf_file, client, dest_lang, model):
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        translate_text = ''
        for page_num in range(len(pdf_reader.pages)):
            print (f"Translating page no. {page_num+1}")
            page = pdf_reader.pages[page_num] 
            content = page.extract_text()
            translate_text += translate_content(client, content, dest_lang, model)+"\n"
    
    return translate_text

def process_docx(docx_file, client, dest_lang, model):
    # Open the Word file
    doc = docx.Document(docx_file)
    
    # Extract the text from each paragraph
    translate_text = ''
    paragraph_no = 1
    for paragraph in doc.paragraphs:
        print (f"Translating paragraph no. {paragraph_no}")
        translate_text += translate_content(client, paragraph.text, dest_lang, model)+"\n"
        paragraph_no += 1
        

    return translate_text

def get_argument_or_env(args, arg_name, env_name):
    value = getattr(args, arg_name)
    if not value:
        value = os.getenv(env_name)
        if not value or value=="":
            value = input(f"Please enter {arg_name.replace('_', ' ')}: ")
    return value

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Translate file content using an OpenAI model.")
    
    parser.add_argument('--dest_lang', type=str, help='The destination language')
    parser.add_argument('--model', type=str, help='The OpenAI model to use')
    parser.add_argument('--input_file', type=str, help='The input file path')
    parser.add_argument('--output_file', type=str, help='The output file path')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Get arguments or prompt for them if not provided
    dest_lang = get_argument_or_env(args, 'dest_lang', 'DEST_LANG')
    model = get_argument_or_env(args, 'model', 'OPENAI_DEPLOYMENT_NAME')
    in_file = get_argument_or_env(args, 'input_file', 'INPUT_FILE')
    out_file = get_argument_or_env(args, 'output_file', 'OUTPUT_FILE')
    
    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_key=os.getenv("OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION")
    )
        
    # Read the content of the input file
    file_extension = os.path.splitext(in_file)[1]
    if file_extension == '.pdf':
        content = process_pdf(in_file, client, dest_lang, model)
    elif file_extension == '.docx':
        # Read the content of the docx file
        content = process_docx(in_file, client, dest_lang, model)
    elif file_extension == '.txt':
        with open(in_file, 'r') as file:
            content = file.read()
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")
    
    PROMPT = os.getenv("PROMPT")
    prompt= PROMPT.format(content=content, dest_lang=dest_lang)
    
    response = client.chat.completions.create(
        model=model,
        messages=[ {"role": "user", "content": prompt}]
    )
   
    translated_text = response.choices[0].message.content
    
    with open(out_file, 'w') as file:
        file.write(translated_text)
    
    print(f"Translation completed and saved to {out_file}")

if __name__ == "__main__":
    main()