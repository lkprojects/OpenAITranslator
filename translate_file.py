import argparse
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import PyPDF2
import docx
import tiktoken
import re

# Using the tokenizer of gpt-4o and gpt-4o-mini for counting tokens
tokenizer = tiktoken.get_encoding("o200k_base")

client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION")
)
        
def count_tokens(text):
    tokens = tokenizer.encode(text)
    return len(tokens)

def split_text_into_chunks(text, max_chunk_size):
    # Split the text into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Check if adding the next sentence would exceed the max_chunk_size
        if count_tokens(current_chunk) + count_tokens(sentence) <= max_chunk_size:
#        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
 
            current_chunk = sentence + " "
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def call_openai(content, dest_lang, model):
    PROMPT = os.getenv("PROMPT")
    prompt= PROMPT.format(content=content, dest_lang=dest_lang)
    
    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def translate_content(content, dest_lang, model, chunk_size=1000):
    chunks = split_text_into_chunks (content, chunk_size)
    chunk_num = 1
    translate_text = ''
    for chunk in chunks:
        print (f"Translating chunk no. {chunk_num}")
        translate_text += call_openai(chunk, dest_lang, model)+"\n"
        chunk_num+=1
    return translate_text
       
def process_pdf(pdf_file):
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        content=''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num] 
            content += page.extract_text()

    return content

def get_argument_or_env(args, arg_name, env_name):
    value = getattr(args, arg_name)
    if not value:
        value = os.getenv(env_name)
        if not value or value=="":
            value = input(f"Please enter {arg_name.replace('_', ' ')}: ")
    return value

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Translate file content using an OpenAI model. Supports PDF and TXT files.")
    
    parser.add_argument('--dest_lang', type=str, help='The destination language code')
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
    
    chunk_size = int(os.getenv("CHUNK_SIZE"))

    # Read the content of the input file
    file_extension = os.path.splitext(in_file)[1]
    if file_extension == '.pdf':
        content = process_pdf(in_file)
    elif file_extension == '.txt':
        with open(in_file, 'r') as file:
            content = file.read()
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")
    
    translated_text = translate_content(content, dest_lang, model, chunk_size)

    with open(out_file, 'w') as file:
        file.write(translated_text)
    
    print(f"Translation completed and saved to {out_file}")

if __name__ == "__main__":
    main()