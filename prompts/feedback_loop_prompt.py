FEEDBACK_LOOP_CORRECTION_PROMPT = """
You will be given JAVA code from an implementation file and Errors occurring while executing the test case.
You will also be given the code for the locator file and the feature file associated with the test case for getting information about the variables and the tasks to be done respectively.
Your task is to fix the errors occurring in the implementation file code and return the fixed code.

The following is the text for the feature file between `---FEATURE-FILE-START---` and `---FEATURE-FILE-END---` 
---FEATURE-FILE-START---
{feature_file_code}
---FEATURE-FILE-END---

The following is the code for the implementation file between `---IMPLEMENTATION-FILE-START---` and `---IMPLEMENTATION-FILE-END---` 
---IMPLEMENTATION-FILE-START---
{implementation_file_code}
---IMPLEMENTATION-FILE-END---

The following is the code for the locator file between `---LOCATOR-FILE-START---` and `---LOCATOR-FILE-END---` 
---LOCATOR-FILE-START---
{locator_file_code}
---LOCATOR-FILE-END---

The following are the Errors occurring in the implementation file  between `---ERROR-START---` and `---ERROR-END---` 
---ERROR-START---
{errors_extracted}
---ERROR-END---


You can use the following instructions in order to fix the errors:
1. First go through the error and understand that in which function does the error occur.
2. Identify the logical error in the function and fix it by adding the required code for fixing the core issue in the function.
3. Take help from the locator file to know the names of the variables associated with the  respective web elements.
4. Take help from the feature file text to confirm what functionality has to be implemented in the function being fixed.

Important Instructions
1. return only the fixed implantation file code and noting else, the code must be returned between the separators `---IMPLEMENTATION-FILE-START---` and `---IMPLEMENTATION-FILE-END---`
2. Fix only the function which is the source of the error.
3. Return the complete implementation file code with all the functions.
4. Give same names to all the functions as 
"""
