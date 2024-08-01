# Azure OpenAI File Translator

This command line program translates PDF and TXT files into any target language using Azure OpenAI LLMs.

## Important notes
- Speed:
   - Translation generates a lot of output tokens (unlike summarization for example). 
   - Note that output tokens are processed slower and are more expensive than input tokens.
- Token generation limitation:
   - The context window of gpt-4 and gpt-4o is 128k tokens for input but only 4096 tokens for output.
   - Translating 4096 tokens in English to a different language (like Chinese) might produce more than 4096 tokens in the output because it is in a different language.
- Working in chunks:
   - To avoid “chopping” the output because of the output limitations described above, I'm calling Azure OpenAI in chunks of sentences that can not exceed `CHUNK_SIZE` tokens(configurable with an environment variable).
   - Each chunk contains whole sentences and is translated individually.
   - The program concatenates the translation results of each chunk to the final output response.
- gpt-4o vs. gpt-4o-mini:
   - Gpt-4o-mini is much cheaper and faster than gpt-4o.
   - The translation quality might NOT be as good as the quality of gpt-4o. That depends on the target language. I recommend to check which model works best for your use case.
   - For gpt-4o-mini, the output window is 16K (unlike gpt-4o where the window is 4K). Therefore, you can increase the chunk size if you wish.
- The program uses the tokenizer of `gpt-4o` and `gpt-4o-mini` to count the tokens. **DO NOT USE ANY OTHER MODEL**.

## Installation
1. Use Python 3.9 or higher.
2. Perform the following:
   ```bash
   pip install -r requirement.txt
   ```
 
### Environment parameters

Set the following parameter in the `.env` file for your environment:

- `OPENAI_DEPLOYMENT_NAME` - The model's deployment name on Azure OpenAI service.
- `AZURE_OPENAI_ENDPOINT` - The Azure OpenAI resource endpoint (URL) 
- `OPENAI_API_KEY` - The Azure OpenAI resource key
- `OPENAI_API_VERSION` - The OpenAI API version used
- `DEST_LANG` - The destination language to which you wish to translate file content (For example: "French").
- `INPUT_FILE` - Source file name
- `OUTPUT_FILE` - Target file name that will contain the translated text
- `PROMPT` - The prompt sent to Azure OpenAI endpoint.

   Example for setting the `PROMPT` parameter:
   ```
   PROMPT="Translate the following text to {dest_lang}:\n\n{content}"
   ```

- `CHUNK_SIZE` sets the number of maximum tokens to send OpenAI in each iteration.

## How to use the application
The program accepts the following arguments:
- `--dest_lang` - The destination language
- `--model` - The OpenAI model to use (set to the deployment name)
- `--input_file` - The file to translate
- `--output_file` - The output file name

If any argument is not set via command line, the program will use the settings in the `.env` file.\
If any argument is not set via command line and not set in the `.env` file, the program will ask the user to enter the missing argument.

