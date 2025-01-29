GET_FILE_CODE_PROMPT = """
    The text contains information about a {file_type} files to be saved
    The text is given between `---FILE-SAVER-TEXT---` and `---FILE-SAVER-TEXT---`
    ---FILE-SAVER-TEXT---
    {text}
    ---FILE-SAVER-TEXT---
    
    Your task is to extract the python code present in the text and return it as JSON in the following format:
    There can only be 2 types of text which can be present in the context which is either code for locators file or code for step-definition and implementation file
    {{
      'locator' : <python code of the locator file extracted>  
    }}
    If the file type is step-definition and implementation then return an output something like this
    {{
      'step_definition' : <python code of the step-definition file extracted>, 
      'implementation_file' : <python code of the implementation file extracted> 
    }}
    
    Important Instructions:
    1. Return only the JSON containing the codes of the file and nothing else
    """
    