import subprocess
from utils.llm_call import call_anthropic_model
from utils.general_utils import extract_text_between_markers
from utils.run_env_creator import JAVA_ROOT,JAVA_ROOT_IMP,JAVA_ROOT_LOC, JAVA_ROOT_STD 
import time
from logger import logger
from prompts.feedback_loop_prompt import FEEDBACK_LOOP_CORRECTION_PROMPT
from dotenv import load_dotenv
import os

load_dotenv()

def extract_errors(output):
    # Define the start marker where the error messages begin
    start_marker = "[ERROR] Errors:"
    
    # Find the start index of the marker
    start_index = output.find(start_marker)
    
    logger.info("Extracting Error from standard output")
    
    # Check if the marker is found in the output
    if start_index != -1:
        # Adjust the index to get content right after the marker
        start_index += len(start_marker)
        
        # Extract everything after the marker
        error_content = output[start_index:]
        
        # Optionally, strip any leading/trailing whitespace
        error_content = error_content.strip()
        
        return error_content
    else:
        # Return None or an appropriate message if the marker is not found
        return "No error section found in the output."


def run_maven_command(directory):
    # Change to the specified directory
    mvn_executable = "C:\\Program Files\\apache-maven-3.9.9\\bin\\mvn.cmd"
    try:
        # Setting cwd (current working directory) in subprocess.run
        result = subprocess.run(
            [mvn_executable, 'clean', 'test'],
            cwd=directory,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        logger.info("JAVA code Execution completed.")
        
        return extract_errors(result.stdout)
        
            
    except Exception as e:
        print(f"An error occurred: {e}")



def feedback_loop_return_corrected_code(limit=1):
    
    
    start_time = time.time()
    
    try:
        limit = int(limit)
    except ValueError:
        logger.error(f"Invalid input for limit: {limit}. Limit must be an integer.")
        return  # Exit the function if limit is not an integer
    
    logger.info(f"Limit Set to : {type(limit)} {limit}")
    
    for _ in range(limit):
        
        
        filepath = JAVA_ROOT
        errors_found = run_maven_command(filepath)
        
        implementation_file_path = JAVA_ROOT_IMP
        locator_file_path = JAVA_ROOT_LOC
        feature_file_path = JAVA_ROOT_STD
        
        with open(implementation_file_path) as f:
            implementation_file_code = f.read()

        with open(locator_file_path) as f:
            locator_file_code = f.read()

        
        with open(feature_file_path) as f:
            feature_file_code = f.read()
        
        
        final_prompt = FEEDBACK_LOOP_CORRECTION_PROMPT.format(feature_file_code=feature_file_code, implementation_file_code=implementation_file_code, locator_file_code=locator_file_code, errors_extracted=errors_found)
        

        llm_res = call_anthropic_model(
            prompt=final_prompt
        )

        logger.info("Prompt Created and Code Fixed for Loop : {cycle}".format(cycle=_+1))
            
        new_imp_code = extract_text_between_markers(llm_res, "---IMPLEMENTATION-FILE-START---", "---IMPLEMENTATION-FILE-END---")
        

        with open(implementation_file_path, 'w') as f:
            f.write(new_imp_code)
            
    end_time = time.time()  


    logger.info(f"Time Taken for Feedback loop with {limit} loops in minutes: {(end_time - start_time)/60.0}")