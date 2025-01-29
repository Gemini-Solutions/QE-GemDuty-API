from utils.llm_call import call_anthropic_model
import json
# from xpath_generator import get_raw_xpath_dictionary
from json_repair import repair_json
from logger import logger
from prompts.segregation_utility import XPATH_SEGREGATION_PROMPT

# TODO: need to test llama-3-170b for this task




def filter_xpaths(extracted_xpaths: dict,reference_xpaths: dict) -> dict:
    
    final_xpaths = dict(extracted_xpaths)
    
    values_to_search = set(list(reference_xpaths.values()))
        
    for element,xpath in extracted_xpaths.items():
        if xpath not in values_to_search:
            final_xpaths[element] = "NULL"


    return  final_xpaths


def xpath_segregator(action:str, element_xpaths:dict)->dict:

    logger.info("Started Xpath Segregation")
    
    element_xpaths_str = json.dumps(element_xpaths).replace('{','{{').replace('}','}}')

    final_xpath_seg_prompt = XPATH_SEGREGATION_PROMPT.format(action_specified=action,element_xpath_dict=element_xpaths_str)
    
    
    xpath_seg_result_str = call_anthropic_model(
        prompt=final_xpath_seg_prompt
    )
    logger.info("Xpath Segregation Completed")
    
    xpath_seg_result_str = repair_json(xpath_seg_result_str)
    xpath_seg_result = json.loads(xpath_seg_result_str)
    
    filtered_xpaths = filter_xpaths(xpath_seg_result, element_xpaths)
    logger.info("Segregated Xpaths Filtered against original")
    return filtered_xpaths
    

# if __name__ == "__main__":
    
#     url =  "https://www.myntra.com/sports-shoes/red+tape/red-tape-men-drift-round-toe-mesh-walking-shoes/29869640/buy"
#     action_type = "No-Login"
#     xpaths_raw = get_raw_xpath_dictionary(url,action_type)
    
#     action = "Click on 'Add to cart' button and then click on 'Go to cart' or 'Cart' button"
#     seg_xpaths = xpath_segregator(action, xpaths_raw)
    
#     print("Segregated Xpaths : \n")
#     print(
#         json.dumps(seg_xpaths, indent=4)
#     )
    
#     filtered_xpaths = filter_xpaths(seg_xpaths, xpaths_raw)
    
#     print("Filtered Xpaths : \n")
#     print(
#         json.dumps(filtered_xpaths, indent=4)
#     )
    

    
    