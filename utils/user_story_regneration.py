from prompts.regenerate_code_user_story import REGENERATE_FEATURE_FILE, CHANGE_TYPE_ROUTER, REGENERATE_USER_STORY
from utils.llm_call import call_anthropic_model
from utils.user_story_parser import generate_testcases_from_user_story_or_description
from utils.run_env_creator import JAVA_ROOT_FT
from logger import logger
import json
def detect_change_type_and_regenerate(instructions, user_story):
    
    change_type_prompt = CHANGE_TYPE_ROUTER.format(instructions=instructions)
    change_type_res = json.loads(call_anthropic_model(change_type_prompt))
    change_type = change_type_res["category"]

    final_res = {
        "change_type": change_type,
        "regenerated_content": None
    }
    
    logger.info(f"Change Type Detected: {change_type}")
    
    if change_type == 'Only Feature':
        with open(JAVA_ROOT_FT, 'r') as file:
            feature_file_text = file.read()
        logger.info(f"Feature File Text Read")
        regenerate_feature_file_prompt = REGENERATE_FEATURE_FILE.format(instructions=instructions, feature_file_text=feature_file_text)
        regenerate_feature_file_res = call_anthropic_model(regenerate_feature_file_prompt)
        logger.info(f"Feature File Regenerated")
        final_res["regenerated_content"] = regenerate_feature_file_res
    else:
        regenerate_user_story_prompt = REGENERATE_USER_STORY.format(instructions=instructions, user_story=user_story)
        regenerated_user_story_res = call_anthropic_model(regenerate_user_story_prompt)
        logger.info(f"User Story Regenerated")
        final_res["regenerated_content"] = regenerated_user_story_res
    
    return final_res


def regenerate_as_per_instructions(instructions, user_story):
    
    change_type_regen = detect_change_type_and_regenerate(instructions, user_story)
    
    if change_type_regen["change_type"] == "Only Feature":
        with open(JAVA_ROOT_FT, 'w') as file:
            file.write(change_type_regen["regenerated_content"])
        logger.info(f"New Feature File Written in same location : {JAVA_ROOT_FT}")
    else:
        user_story = change_type_regen["regenerated_content"]
        logger.info(f"User story passed for code Regeneration")
        generate_testcases_from_user_story_or_description(user_input=user_story,input_type='user_story')
    
    logger.info(f"Code Regeneration Completed")
     