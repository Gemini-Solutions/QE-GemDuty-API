CHANGE_TYPE_ROUTER="""
Assume there is a feature file, a step definition and a implementation file for testing a particular scenario, your task is to categorize the instructions in any of the following categories:
1. All: If the instruction has an addition of a new step in the feature file which hence forth requires changes to be done in the step definition and implementation file.
2. Only Feature: If the instruction require changes in the feature file but not in the implementation file and step definition file. For example, adding a new example in the feature file.

The instructions to be categorized are given below the markers `---START-INSTRUCTIONS---` and `---END-INSTRUCTIONS---`.
---START-INSTRUCTIONS---
{instructions}
---END-INSTRUCTIONS---

Important points to note:
1. The output should be a JSON for the following format:
{{
"category" : <All or Only feature>
"justification" : <justification for the category>
}}
2. Return only the JSON and nothing else.

You can use the following examples for clarity:
Category: All
(New step added in the feature file, requiring updates to step definitions and implementation)

Instruction: "Add a step to validate the error message when the user enters an invalid password."
    Feature File: Add Then an "Invalid password" error should appear.
    Step Definition: Add a regex-matching function for the new step.
    Implementation: Write code to check the error message.
Output:
{{
  "category": "All",
  "justification": "Adding new step 'Then an \"Invalid password\" error should appear' requires corresponding step definition and implementation code to validate error messages"
}}

Instruction: "Include a step to navigate to the settings page before submitting the form."
    Feature File: Add Given I am on the settings page.
    Step Definition/Implementation: Define navigation logic and link it to the step.
Output:
{{
  "category": "All",
  "justification": "New navigation step 'Given I am on the settings page' needs step definition mapping and implementation logic for page navigation"
}}

Instruction: "Verify the total cart price after applying a discount coupon."
    Feature File: Add Then the total price should reflect a 10  discount.
    Step Definition/Implementation: Implement discount calculation and assertion.
Output:
{{
  "category": "All",
  "justification": "Verification step for discount calculation requires new assertion logic in implementation file and step definition pattern update"
}}

Instruction: "Add a step to upload a profile picture during registration."
    Feature File: Add When I upload "profile.jpg" as my profile picture.
    Step Definition/Implementation: Handle file upload logic.
Output:
{{
  "category": "All",
  "justification": "File upload step 'When I upload \"profile.jpg\"...' needs new file handling implementation and step definition regex"
}}

Instruction: "Check if the user’s account is locked after 3 failed login attempts."
    Feature File: Add Then the account should be locked.
    Step Definition/Implementation: Implement account-lock validation.
Output:
{{
  "category": "All",
  "justification": "Account lock verification requires new validation logic in implementation and step definition for the assertion"
}}

Category: Only Feature
(Changes limited to the feature file)

Instruction: "Add a new example to test login with a non-registered email."
    Feature File: Add a new row under Examples: with test@example.com and Password123.
Output:
{{
  "category": "Only Feature",
  "justification": "Adding new example row uses existing steps/patterns and requires no code changes"
}}

Instruction: "Update the existing scenario to include a tag @smoke."
    Feature File: Add @smoke above the scenario name.
Output:
{{
  "category": "Only Feature",
  "justification": "Adding @smoke tag is metadata change that doesn't affect step definitions or implementation"
}}

Instruction: "Rename the scenario from 'Successful Login' to 'User Login with Valid Credentials'."
    Feature File: Update the scenario title only.
Output:
{{
  "category": "Only Feature",
  "justification": "Scenario renaming only affects feature file structure without changing step logic"
}}
Instruction: "Add a new scenario outline to test checkout with different payment methods (Credit Card, PayPal)."
    Feature File: Add a new Scenario Outline with Examples for payment methods (no new steps).
Output:
{{
  "category": "Only Feature",
  "justification": "New scenario outline with payment methods uses existing steps with different examples"
}}

"""



REGENERATE_USER_STORY = """
You will be given a user story which is a combinations of URLs and actions that are supposed to be performed on the URLs. There would also be a set of instructions which would be given to you. You need to regenerate the user story based on the instructions given to you.

The user story is given below between  the markers `---START-USER-STORY---` and `---END-USER-STORY---`
---START-USER-STORY---
{user_story}
---END-USER-STORY---

The instructions are given below between the markers `---START-INSTRUCTIONS---` and `---END-INSTRUCTIONS---`
---START-INSTRUCTIONS---
{instructions}
---END-INSTRUCTIONS---

You can use the following instructions to regenerate the user story based on the instructions given to you.
1. Go through the instructions and identify the changes that need to be made in the user story.
2. Update the user story with the changes based on the instructions.
3. if a URL is present in the instruction then add it to the appropriate place prefixing the same with `redirect to : <URL mentioned in the instructions>`

Important instructions:
1. While updating the user story as per the instructions maintain the old instructions already present in the user story
2. Do not return anything other than the regenerated user story.
"""

REGENERATE_FEATURE_FILE="""
You will be given a text of a feature file in gherkin syntax and a set of instruction about the changes that need to be made in the feature file, you need to regenerate the feature file text based on the instructions about the change to be made in the feature file.

The feature file text is given below the markers `---START-FEATURE-FILE---` and `---END-FEATURE-FILE---`
---START-FEATURE-FILE---
{feature_file_text}
---END-FEATURE-FILE---

The instructions are given below the markers `---START-INSTRUCTIONS---` and `---END-INSTRUCTIONS---`
---START-INSTRUCTIONS---
{instructions}
---END-INSTRUCTIONS---

You can use the following instructions in order to update the feature file as per the instructions given to you.
1. Go through the instructions and identify the changes that need to be made in the feature file.
2. Update the feature file with the changes based on the instructions.
3. If the instructions are about adding some examples in the feature file, then add relevant examples in the feature file text.
4. Only make the changes where it is required and keep rest of the feature file text as it is.

Important instructions:
1. Return only the regenerated feature file code and nothing else
2. Only update the required part of the feature file text and keep the rest of the feature file text as it is.

You can use the following examples as a reference:
Example 1
Input Feature File:
Feature: User Login  
  Scenario Outline: Login with valid credentials  
    Given I am on the login page  
    When I enter "<username>" and "<password>"  
    Then I should see the dashboard  

    Examples:  
      | username | password |  
      | user1    | pass123  |  
      
Instruction:
"Add a new example with username=user2 and password=pass456"

Output:   
Feature: User Login  
  Scenario Outline: Login with valid credentials  
    Given I am on the login page  
    When I enter "<username>" and "<password>"  
    Then I should see the dashboard  

    Examples:  
      | username | password |  
      | user1    | pass123  |  
      | user2    | pass456  |  
      
Example 2
Input Feature File:
Feature: Product Search  
  Scenario: Search by product name  
    Given I open the search page  
    When I search for "laptop"  
    Then results containing "laptop" are shown  
    
Instruction:
"Add tag @smoke to this scenario"

Output:
Feature: Product Search  
  @smoke  
  Scenario: Search by product name  
    Given I open the search page  
    When I search for "laptop"  
    Then results containing "laptop" are shown  
"""


REGENERATE_FEATURE_FILE_IMPLEMENTATION_FILE ="""
You will be given a text of a feature file in gherkin syntax, the code of an implementation file and a set of instruction about the changes that need to be made in the feature file, you need to regenerate the code of the implementation file code and feature file text based on the instructions about the change to be made in the feature file. 

The feature file text is given below the markers `---START-FEATURE-FILE---` and `---END-FEATURE-FILE---` 

---START-FEATURE-FILE---
{feature_file_text}
---END-FEATURE-FILE---

The implementation file code is given below the markers `---START-IMPLEMENTATION-FILE---` and `---END-IMPLEMENTATION-FILE---`.

---START-IMPLEMENTATION-FILE---
{implementation_file_code}
---END-IMPLEMENTATION-FILE---

The instructions are given below the markers `---START-INSTRUCTIONS---` and `---END-INSTRUCTIONS---`.
---START-INSTRUCTIONS---
{instructions}
---END-INSTRUCTIONS---

You can use the following instruction to regenerate the code of the implementation file based on the instructions about the changes to be made in the feature file.
1. Go through the instructions and identify the changes that need to be made in the feature file.
2. Make the changes in the feature file text, based on the instructions.
3. Regenerate the code of the implementation file based on the changes made in the feature file text
4. If the instructions are about adding some examples in the feature file, then add relevant examples in the feature file text and regenerate the code of the implementation file based on the examples added in the feature file text.
5. If the instructions are about adding some steps in the feature file, then add relevant steps in the feature file text and regenerate the code of the implementation file based on the steps added in the feature file text.

Important instructions:
1. The regenerated feature file code must be between markers `---START-FEATURE-FILE---` and `---END-FEATURE-FILE---`.
2. The regenerated implementation file code must be between markers `---START-IMPLEMENTATION-FILE---` and `---END-IMPLEMENTATION-FILE---`.
3. Do not return anything other than the regenerated feature file code and implementation file code.
"""