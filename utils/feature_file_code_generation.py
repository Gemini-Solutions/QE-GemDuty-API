from utils.user_story_parser import generate_testcases_from_user_story_or_description
import re
from dotenv import load_dotenv
import os
from logger import logger


load_dotenv()


def combine_scenarios(scenario_list):
    combined_scenarios = []
    i = 0
    while i < len(scenario_list):
        current_string = scenario_list[i]
        # Check if the current string is a scenario
        if 'Scenario Outline:' in current_string or 'Scenario:' in current_string:
            scenario = current_string
            i += 1
            # Collect all content until the next scenario or end of list
            while i < len(scenario_list):
                next_string = scenario_list[i]
                if 'Scenario Outline:' in next_string or 'Scenario:' in next_string:
                    break
                else:
                    scenario += '\n' + next_string
                    i += 1
            combined_scenarios.append(scenario)
        else:
            i += 1
    return combined_scenarios



def generate_test_cases_feature_file(file_path):
    
    with open(file_path) as f:
        feat_file_text = f.read()
    
    feat_file_text_chunks = re.split(r'\n{2,}', feat_file_text)

    background_text = ""
    if "Feature:" in feat_file_text_chunks[0]: 
        if "Background:" in feat_file_text_chunks[1]:
            background_text = feat_file_text_chunks[0] + feat_file_text_chunks[1]
            feat_file_text_chunks = feat_file_text_chunks[2:]
        else:
            background_text = feat_file_text_chunks[0]
            feat_file_text_chunks = feat_file_text_chunks[1:]
    
 
    proc_feat_file_text_chunks = combine_scenarios(feat_file_text_chunks)     

    feat_file_user_stories = []
    
    for text in proc_feat_file_text_chunks:    
        text = background_text + text
        feat_file_user_stories.append(text)
    
    
    dir_paths = []
    for index,user_story in enumerate(feat_file_user_stories):

        dir_name = f"Feature_File_Scenario_{index+1}"
        dir_path = os.path.join("complete-flow-runs",dir_name)
        
        os.makedirs(dir_path, exist_ok=True)
        
        with open(f"{dir_path}//user_story.txt", "w") as f:
            f.write(user_story)
        
        generate_testcases_from_user_story_or_description(user_input=user_story,input_type="user story", dir_name=dir_name)
        
        dir_paths.append(dir_path)
    
    
    return dir_paths