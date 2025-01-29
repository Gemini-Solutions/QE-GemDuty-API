import json
import os
from prompts.reply_prompts import GREETING_REPLY_PROMPT, SIMPLE_INSTRUCTIONS_REPLY_PROMPT
import subprocess
from utils.run_env_creator import JAVA_ROOT_LOC, JAVA_ROOT_FT, JAVA_ROOT_IMP, JAVA_ROOT_STD
def is_maven_installed():
    try:
        # Run the command 'mvn --version'
        result = subprocess.run(["mvn", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # If the command runs successfully, Maven is installed
        if result.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        # If running the command 'mvn' results in FileNotFoundError, Maven is not installed
        return False

def extract_text_between_markers(input_text:str, start_marker:str, end_marker:str)->str:

    # Finding the start and end indices of the markers
    start_index = input_text.find(start_marker) + len(start_marker)
    end_index = input_text.find(end_marker, start_index)

    # If either marker is not found, return an empty string
    if start_index == -1 or end_index == -1:
        return ""

    # Extracting the text between the markers
    return input_text[start_index:end_index].strip()


def prepare_reply(classified_type:str, missing_params:str)->str:
    
    if classified_type == 'simple instructions':
        return SIMPLE_INSTRUCTIONS_REPLY_PROMPT.format(missing_params=missing_params)
    else:
        return GREETING_REPLY_PROMPT
    

def read_all_files():
    """
    read the feature, step definition, locator and implementation file and return a tuple in order 
    feature_file, locator_file, step_definition_file, implementation_file
    """
    with open(JAVA_ROOT_FT,"r") as file:
        feature_file = file.read()
    
    with open(JAVA_ROOT_LOC,"r") as file:
        locator_file = file.read()
    
    with open(JAVA_ROOT_STD,"r") as file:
        step_definition_file = file.read()
    
    with open(JAVA_ROOT_IMP,"r") as file:
        implementation_file = file.read()
    
    return {"status" : 200, "message" : (feature_file, locator_file, step_definition_file, implementation_file)}