import sys
import os
import concurrent.futures
import streamlit as st
from functions.config import (
    CHATGPT_SUMMARIZER_CONFIG,
    LLAMA_SUMMARIZER_CONFIG,
    CLAUDE_SUMMARIZER_CONFIG,
)

# Add the path to YourProject to sys.path
project_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_path)

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language,
)
from utils.llm import call_llm, call_aws_bedrock_llm, call_anthropic_model

# Summarizer prompt
SUMMARIZER_PROMPT = """
Examine the HTML code snippet provided below:
{CODE_BLOCK}

Compose a concise, non-technical summary without delving into HTML, CSS, or JavaScript details. \
Describe the overall functionality of the code and highlight the visible elements, avoiding technical language. \
Do not provide information related to the underlying technologies; focus solely on the code's purpose and the elements it presents.

Additional Considerations:
1. Content Structure: Mention if there's a discernible structure or hierarchy within the code.
2. User Interface Elements: Identify and describe any visible components or elements that users may interact with.
3. Functionality: Summarize the primary purpose or function of the code, focusing on its intended outcomes.
"""


# Function to process each chunk of HTML and generate a summary
def process_html_chunk(html_chunk, config, llm):
    prompt = SUMMARIZER_PROMPT.format(CODE_BLOCK=html_chunk.page_content)

    # Call the appropriate LLM based on the provided llm model
    if llm.startswith("ChatGPT"):
        llm_output = call_llm(
            conversation=prompt,
            model=config["model"],
            temperature=config["temperature"],
            response_format=config["response_format"],
        )
    elif llm.startswith("Llama"):
        llm_output = call_aws_bedrock_llm(
            prompt=prompt, model=config["model"], temperature=config["temperature"]
        )
    else:
        llm_output = call_anthropic_model(
            prompt=prompt, model=config["model"], temperature=config["temperature"]
        )

    # Process the LLM output and return the generated summary
    if llm_output["finish_reason"] == "stop":
        if llm.startswith("ChatGPT"):
            return llm_output["response_generated"].content
        else:
            return llm_output["response_generated"].strip()

    return ""


# Main function to split the HTML code and summarize the content
def summarizer_function(html_code_block, config, llm):
    # Create the HTML splitter
    html_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.HTML,
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
    )

    # Split the HTML into chunks
    html_docs = html_splitter.create_documents([html_code_block])

    # Use multithreading to process the chunks concurrently
    summary_list = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit each chunk for processing
        futures = [
            executor.submit(process_html_chunk, html_chunk, config, llm)
            for html_chunk in html_docs
        ]

        # Collect results as they complete
        for future in concurrent.futures.as_completed(futures):
            try:
                summary = future.result()
                summary_list.append(summary)
            except Exception as e:
                print(f"Error processing chunk: {e}")

    # Join the individual summaries to form the final summary
    final_summary = "".join(summary_list)

    return final_summary


# Streamlit cached function to avoid recomputation for the same HTML block and LLM
@st.cache_data(ttl="8h")
def st_summarizer_function(html_code_block, llm):
    # TODO : refactor - have just one function
    # Select the appropriate configuration based on the LLM type
    if "gpt" in llm.lower():
        config = CHATGPT_SUMMARIZER_CONFIG
    elif "llama" in llm.lower():
        config = LLAMA_SUMMARIZER_CONFIG
    else:
        config = CLAUDE_SUMMARIZER_CONFIG

    # Generate the summary
    return summarizer_function(html_code_block, config, llm)