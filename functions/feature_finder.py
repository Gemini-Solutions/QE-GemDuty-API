import sys
import os
import re
import json
import concurrent.futures
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language,
)
from utils.scrapper import scrape_website_from_url
from utils.llm import call_llm, call_aws_bedrock_llm, call_anthropic_model
from utils.error_handlers import MissingFeature
import streamlit as st
from functions.config import (
    CHATGPT_FEATURE_FINDER_CONFIG,
    LLAMA_FEATURE_FINDER_CONFIG,
    CLAUDE_FEATURE_FINDER_CONFIG,
)

# Add the path to YourProject to sys.path
project_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_path)
# TODO : move to ./prompts
# Feature extraction prompt
FEATURE_FINDER_PROMPT = """
You will be provided with HTML code. Your objective is to identify all possible functional test cases, considering both positive and negative scenarios.

Output Format: Present the extracted information in only JSON format as follows:

{{
  "feature": [
    {{"name": "Feature Name 1", "description": "Description of the feature functionality 1.", "xpath": "xpath_expression_1"}},
    {{"name": "Feature Name 2", "description": "Description of the feature functionality 2.", "xpath": "xpath_expression_2"}},
    // ... (for additional features)
  ]
}}

Xpath expression for reference purpose is given below:
1. //tagname[contains(@attribute,'value')]
2. //tagname[@attribute='value']
3. //tagname[contains(text(),'visible text')]

Note:
1. Do not include features or functionalities that are not present in the HTML code.
2. Do not generate test cases for elements that are not visible.
3. Do not repeat test cases.
4. Do not hallucinate.
5. Do not blindly copy the xpath expressions. Create valid xpaths by yourself.

Here is the HTML Code: 
{HTML_CODE}
"""

# TODO :  find duplicate - refactor - send to general_utils
# Function to process each chunk of HTML in parallel
def process_html_chunk(html_chunk, config, llm):
    prompt = FEATURE_FINDER_PROMPT.format(HTML_CODE=html_chunk.page_content)

    # Call the appropriate LLM based on the provided llm model
    if "gpt" in llm.lower():
        llm_output = call_llm(
            conversation=prompt,
            model=config["model"],
            temperature=config["temperature"],
            response_format=config["response_format"],
        )
    elif "llama" in llm.lower():
        llm_output = call_aws_bedrock_llm(
            prompt=prompt, model=config["model"], temperature=config["temperature"]
        )
    else:
        llm_output = call_anthropic_model(
            prompt=prompt, model=config["model"], temperature=config["temperature"]
        )

    # Process the LLM output
    if llm_output["finish_reason"] == "stop":
        if "gpt" in llm.lower():
            chunk_feature_dict = json.loads(llm_output["response_generated"].content)
        else:
            json_match = re.search(
                r"\{.*\}", llm_output["response_generated"], re.DOTALL
            )
            if json_match:
                json_str = json_match.group()
                chunk_feature_dict = json.loads(json_str)
            else:
                raise MissingFeature()

        # Return the features found in the chunk
        if "feature" in chunk_feature_dict:
            return chunk_feature_dict["feature"]
        else:
            raise MissingFeature()

    return []


# Main function to scrape the website and extract features
def scrape_and_extract_features(url, config, llm):
    # Scrape the website
    html_text = scrape_website_from_url(url)

    # Create the HTML splitter
    html_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.HTML,
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
    )

    # Split the HTML into chunks
    html_docs = html_splitter.create_documents([html_text])

    # Use multithreading to process chunks concurrently
    feature_dict_list = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit each chunk for processing
        futures = [
            executor.submit(process_html_chunk, html_chunk, config, llm)
            for html_chunk in html_docs
        ]

        # Collect results as they complete
        for future in concurrent.futures.as_completed(futures):
            try:
                features = future.result()
                feature_dict_list.extend(features)
            except Exception as e:
                print(f"Error processing chunk: {e}")

    return feature_dict_list, html_text


# Streamlit cached function to avoid recomputation for the same URL and LLM
@st.cache_data(ttl="8h")
def st_scrape_and_extract_features(url, llm):
    # Select the appropriate configuration based on the LLM type
    # TODO : refactor
    if "gpt" in llm.lower():
        config = CHATGPT_FEATURE_FINDER_CONFIG
    elif "llama" in llm.lower():
        config = LLAMA_FEATURE_FINDER_CONFIG
    else:
        config = CLAUDE_FEATURE_FINDER_CONFIG

    # Scrape and extract features
    return scrape_and_extract_features(url, config, llm)
