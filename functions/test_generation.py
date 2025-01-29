import sys
import os
import re
import streamlit as st
# Add the path to YourProject to sys.path
project_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_path)

from utils.llm import call_llm, call_aws_bedrock_llm, call_anthropic_model
from functions.config import (
    CHATGPT_TEST_GEN_CONFIG,
    LLAMA_TEST_GEN_CONFIG,
    CLAUDE_TEST_GEN_CONFIG,
)
# TODO : send to ./prompts
INITIAL_TEST_GEN_PROMPT = """
Create Gherkin syntax-based features for the following page/feature description:
{FEATURE_SUMMARY}

Important Notes: 
- Generate common possible scenarios that should cover the complete functional testing. Keep background description as given in example.
For example: To test the login functionality, possible scenarios can be:
a. user is logged in when enter correct credentials are used.
b. Correct warning/error appears when user enters incorrect credentials to login.
This is just an example. Do not blindly copy this.
If you can not think of any possible scenario, then generate atleast two different and unique scenarios in details.
- Also keep the output in JSON format as given below:
{{
"feature_title": "Title of the Feature",
"feature_description": "Description of the feature",
"background_description": "The application is open in a web browser",
"scenarios_list": [
    {{
    "scenario_title": "Title of the Scenario",
    "scenario_description": "Description of the scenario",
    "steps": [
        "Given [Preconditions or initial context]",
        "When [Actions taken by the user or system]",
        "Then [Expected outcomes or results]",
        # Additional steps or variations can be included using And, But, etc.
        "And [Another action or check]"
        "But [Exception or negation of a previous step]"
    ]
    }},
    {{
    # Scenario 2
    }}
]
}}
"""

ADD_TEST_GEN_PROMPT = """
Create additional distinct scenario not covered above.
Keep the following format:
{{
"scenarios_list": [
    {{
    "scenario_title": "Title of the Scenario",
    "scenario_description": "Description of the scenario",
    "steps": [
        "Given [Preconditions or initial context]",
        "When [Actions taken by the user or system]",
        "Then [Expected outcomes or results]",
        # Additional steps or variations can be included using And, But, etc.
        "And [Another action or check]"
        "But [Exception or negation of a previous step]"
    ]
    }}
}}
"""
# TODO : find duplicate - fix implementation 
def create_initial_test_case(code_block_summary, config, llm):
    prompt = INITIAL_TEST_GEN_PROMPT.format(FEATURE_SUMMARY = code_block_summary)

    messages = [
        {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
        {"role": "user", "content": prompt}
    ]

    if "gpt" in llm.lower():
        llm_output = call_llm(
            conversation=messages,
            model=config['model'],
            temperature=config['temperature'],
            response_format=config['response_format']
        )
    elif "llama" in llm.lower():
        llm_output = call_aws_bedrock_llm(
            prompt=prompt, model=config["model"], temperature=config["temperature"]
        )
    else:
        llm_output = call_anthropic_model(
            prompt=prompt, model=config["model"], temperature=config["temperature"]
        )

    if llm_output['finish_reason'] == 'stop':
        if "gpt" in llm.lower():
            test_generated = llm_output['response_generated'].content
            # test_generated = json.loads(test_generated)
            messages.append({'role': 'assistant', 'content': test_generated})

        else:
            json_match = re.search(
                    r"\{.*\}", llm_output["response_generated"], re.DOTALL
            )

            if json_match:
                json_str = json_match.group()

            test_generated = json_str
            messages.append({'role': 'assistant', 'content': test_generated})

    return test_generated, messages

def create_additional_test_case(messages, config, llm):

    prompt = ADD_TEST_GEN_PROMPT
    messages.append({'role': 'user', 'content': prompt})

    if "gpt" in llm.lower():
        llm_output = call_llm(
            conversation=messages,
            model=config['model'],
            temperature=config['temperature'],
            response_format=config['response_format']
        )
    elif "llama" in llm.lower():
        llm_output = call_aws_bedrock_llm(
            prompt=prompt, model=config["model"], temperature=config["temperature"]
        )
    else:
        llm_output = call_aws_bedrock_llm(
            prompt=prompt, model=config["model"], temperature=config["temperature"]
        )

    if llm_output['finish_reason'] == 'stop':
        if "gpt" in llm.lower():
            new_test_generated = llm_output['response_generated'].content
            messages.append({'role': 'assistant', 'content': new_test_generated})

        else:
            new_test_generated = llm_output["response_generated"]
            messages.append({"role": "assistant", "content": new_test_generated})

    return new_test_generated, messages


@st.cache_data(ttl="8h")
def st_create_initial_test_case(code_block_summary, llm):
    # Select the appropriate configuration based on the LLM type
    if "gpt" in llm.lower():
        config = CHATGPT_TEST_GEN_CONFIG
    elif "llama" in llm.lower():
        config = LLAMA_TEST_GEN_CONFIG
    else:
        config = CLAUDE_TEST_GEN_CONFIG

    # Scrape and extract features
    return create_initial_test_case(code_block_summary, config, llm)


@st.cache_data(ttl="8h")
def st_create_additional_test_case(messages, llm):
    # Select the appropriate configuration based on the LLM type
    if "gpt" in llm.lower():
        config = CHATGPT_TEST_GEN_CONFIG
    elif "llama" in llm.lower():
        config = LLAMA_TEST_GEN_CONFIG
    else:
        config = CLAUDE_TEST_GEN_CONFIG

    # Scrape and extract features
    return create_additional_test_case(messages, llm)
