from utils.llm_call import call_anthropic_model
from json_repair import repair_json
import json
from logger import logger
from prompts.redirection_url_utility import VARIABLE_NAME_REPLACE_PROMPT, ACTION_REDIRECTION_LINK

# TODO: need to test llama-3-170b for this task - FUTURE WORK - COST DECREASE


def redirection_url_finder(task_description : str) -> list:
    
    base_json_extract_prompt = ACTION_REDIRECTION_LINK.format(task_description=task_description)
    
    base_json_str = call_anthropic_model(
        prompt=base_json_extract_prompt
    )
    
    base_json_str = repair_json(base_json_str)
    base_json = json.loads(base_json_str)
    
    logger.info(f"base json : \n{json.dumps(base_json, indent=4)}")
    
    base_json_extend_prompt = VARIABLE_NAME_REPLACE_PROMPT.format(task_description=task_description,json=base_json_str)
    
    extended_json_list_str = call_anthropic_model(
        prompt=base_json_extend_prompt
    )    
    
    extended_json_list_str = repair_json(extended_json_list_str)
    extended_json_list = json.loads(extended_json_list_str)
    
    logger.info(f"Extended JSON : \n{json.dumps(extended_json_list, indent=4)}")
    
    return extended_json_list


# if __name__ == "__main__":
    
#     td = """
#     Scenario Outline : User searches for "shoes", adds it to card and confirms
#     User is at https://www.myntra.com and searches for "shoes"
#     redirected to : https://www.myntra.com/shoes?rawQuery=shoes
#     User Selects the first shoe 
#     redirected : https://www.myntra.com/sports-shoes/red+tape/red-tape-men-drift-round-toe-mesh-walking-shoes/29869640/buy
#     User clicks on Add to cart and the moves to cart
#     redirected to : https://www.myntra.com/checkout/cart
#     User clicks on place order
#     """
    
#     extended = redirection_url_finder(td)
    
    