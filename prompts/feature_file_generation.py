WORK_ITEM_TO_FF_AZURE_JIRA_DESC = """
    You will be given detailed descriptions of tasks assigned to different people as a part of discussion for testing a website for Quality assurance.
    Your task will be to convert each description into a scenario outline for testing the user interactions on the specified website. 

    The detailed description is given between `---DESCRIPTION-START---` and `---DESCRIPTION-END---`

    ---DESCRIPTION-START---
     {work_items_str}
    ---DESCRIPTION-END---

    You need to follow the below instructions for completing the task:
    1. Go through the task description and identify the steps that need to be covered for generating a scenario outline, it can be divided into 2 steps background : which will contain the steps to be done before performing the main task like login or sign-in and Scenario outline : which contains the steps to be performed for testing the main functionality described in the task description, if there are no steps to be assigned to the background then make only the scenario outline
    2. Use the task description to identify single action steps for the background and for the scenario outline : single action step means each step containing just a single action 
    3. Using the task description also identify and mention the URLs to which user will get redirected while performing the steps and mention it after the single action step in which redirection occurs.
    
    Important instructions:  
    1. Identify the Website URL: Extract and highlight the website URL if mentioned, and use it as the base context for all scenarios.
    2. Identify the overall action that has to be completed using the description1
    3. Outline the User Journey: The descriptions must be consolidated into one summary containing all the necessary steps that need to be followed to complete the overall task that has to be completed, the steps must be neither too less nor too more.
    4. Specify Actual Names and Identifiers:
    - Clearly name any buttons, links, or placeholders mentioned in the description. Use quotes to denote the exact labels or text on these UI elements.
    - If specific items are to be interacted with (like 'Noir Jacket' or 'Grey Jacket'), use these exact names in the scenario outline.
    4. Include Examples for Multiple Cases: If the task involves multiple items or variations, include a table of examples at the end of the scenario. Each row should represent a different case, clearly listing any relevant specifics like item names. Mention the item name for which example is given as a variable enclosed in < and >, include the examples section only if it is required else dont include it.
    5. Return only the summarization with the tasks, do not return anything else, start with background section and end with example section (if it is required, else end with the scenario section)
    
    **Example Input**:
    "Implement and test the user interaction on the landing page of https://sauce-demo.myshopify.com/ to ensure that when a user clicks on an item name (e.g., Noir Jacket : https://sauce-demo.myshopify.com/collections/frontpage/products/noir-jacket ), they are redirected to the respective product page. This involves adjusting the UI to make item names clickable and ensuring that the redirect functionality is correctly set up. Acceptance Criteria: Clicking on an item name on the landing page redirects to the product page. Ensure compatibility with major browsers (Chrome, Firefox, Safari). UI elements should be accessible and responsive."

    **Example Output**:
    Scenario outline : Test item selection on sauce-demo-shopify
    User is on the landing page : https://sauce-demo.myshopify.com/
    When user clicks on the 'Noir jakcet' on the landing page
    Then user is redirected to the product page : https://sauce-demo.myshopify.com/collections/frontpage/products/noir-jacket


    Apply these steps to convert detailed task descriptions into concise, structured scenario outlines for testing.
    """


USER_STORY_CONVERSION_PROMPT="""
You will be given a set of instructions for completing an action or a set of actions on a website, the description shall contain actions performed on web elements, whose names will be mentioned in the description
Your task is to create a feature file in gherkin syntax which will be used for performing Automation testing on the website by performing these actions on different web pages.    

The following is the TASK-DESCRIPTION given between `---TASK-DESCRIPTION-START---` and `---TASK-DESCRIPTION-END---`:
---TASK-DESCRIPTION-START---
{user_story}
---TASK-DESCRIPTION-END---

You need to follow the below instruction for completing the task:
1. go through the given task description between the separators `---TASK-DESCRIPTION-START---` and `---TASK-DESCRIPTION-END---`
2. Identify the names of the elements in each of the instructions and the particular actions associated with each of the elements
3. Break the instructions in a way that for each line in the feature file one action and one element is covered
4. for every broken down instruction convert the instruction into gherkin syntax 
5. Include only the first URL given in the instructions,  for the rest which infer redirection from one webpage to another include a line in gherkin syntax which infers about redirection. 

Important instructions
1. Do not return anything other than the gherkin syntax
2. Make use of the word `User` for specifying user in the feature file
3. If the actions specify log-in/authentication and then performing other actions the segregate the authentication part in Background part of feature file
4. If no Examples are given the return the gherkin syntax for whatever value is given

The following is an example of how this can be done 

Sample Input:
URL: https://www.amazon.in/ 

Feature: Add Books in the cart from Amazon

Scenario Outline: Search 'book' From Amazon website
Given user Search 'book' in the Search Box
And user add First 'book' in the cart
When user add item to the cart


The output for the above will be as follows:

Feature: Add Items to Cart on https://www.amazon.in
As a user, I want to search for various items on Amazon and add them to my cart

Scenario: Search and Add Book to Cart
    Given user is on the Amazon homepage
    When user searches for 'Book' in the search box
    And user selects the first 'Book' from the search results
    And user clicks on 'Add to Cart' button
    Then the 'Book' should be added to the user's cart
"""
