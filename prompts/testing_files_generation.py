LOCATOR_FILE_GEN_PROMPT=  """
        The following is a JSON between `---XPATH-START---` and `---XPATH-END---` which contains Xpaths for elements in a website
        ---XPATH-START---
        {xpath_string}
        ---XPATH-END---
        
        Assuming the above given xpaths are accurate and your task is to generate a simple locator file for the above given xpaths

        Important instructions
        1. Just generate the locator file and nothing else, there is no need for verification using python script
        2. Ensure all relevant import statements are present in the code
    """
    
    
PYTHON_CODE_GEN_PROMPT = """
    ---FEATURE-FILE-START---
    {feature_file_text}

    ---FEATURE-FILE-END---

    the feature file is given between `---FEATURE-FILE-START---` and `---FEATURE-FILE-END---`
    Your task will be to implement the step definition file using the above given feature file text in PYTHON

    You can use the following instructions for generating step definition and implementation files
    1. Go through and understand the text of the feature file to comprehend the steps that need to be implemented.
    2. Step definition file will contain the Python code that defines the steps for the feature file text 
    3. the implementation file will contain the actual implementation of the test case / feature file containing the imports from step definition file.
    4. Divide feature file big task into small steps / tasks and implement the functions for getting the steps done
    5. Implement all the functions in the implementation and step definition files for completing the task
   
    use the following as locators as Xpaths for implementing the step definition file for accessing the element 
    The Xpaths are given between `---XPATH-START---` and `---XPATH-END---`

    ---XPATH-START---
    {xpath_string}
    ---XPATH-END---

    Important instructions:
    1. Save the code for the implementation and step definition files using a simple python script, do not use terminal for writing in files.
    2. The Xpaths given are accurate hence do not generate on your own
    3. Do not use chromedriver.exe for accessing the browser instead use WebDriverManager library for the same. 
    4. Include waiting time if the code needs to redirect to some other page and a wait time is required for successful code execution
    5. If the feature file contains the action of verification of element then use Selenium Assertion in JAVA for implementing a function which will can locate the element, an assertion to verify the element as per scenario requirement, exception handling if the element is not found and relevant comments.
    """