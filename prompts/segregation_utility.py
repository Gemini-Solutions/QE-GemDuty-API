XPATH_SEGREGATION_PROMPT = """
You will be given a an action or series of actions to be performed on a webpage, along with this you will also be given a dictionary containing names of elements present on the webpage against their corresponding xpaths
Your task will be to identify the relevant elements as per the actions specified and return a JSON with key as the an intuitive name for the elements and the value being the xpath of the corresponding element

the following is the description of the action given between `---ACTION-DESCRIPTION---` and `---ACTION-DESCRIPTION---` 

---ACTION-DESCRIPTION---
{action_specified}
---ACTION-DESCRIPTION---

the following is the element to xpath dictionary given between `---ELEMENT-XPATH-DICTIONARY---` and `---ELEMENT-XPATH-DICTIONARY---`

---ELEMENT-XPATH-DICTIONARY---
{element_xpath_dict}
---ELEMENT-XPATH-DICTIONARY---

You can use the following instructions for completing the task:
1. Go through the action description and identify elements on which the actions are being performed and infer a name for the identified elements 
2. Go through the element xpath dictionary and identify the names of the element which best matches with the name of the element inferred in the previous step and extract the xpath for the element identified, if there are more than one elements in the xpath dictionary which are matching then choose the one on which action can be performed
3. If no match is found in the previous step then assign null to xpath for the element
4. Make a JSON with element name (inferred or as mentioned in xpath dictionary whichever is more intuitive) against xpath extracted in the previous step 

Important instructions:
1. Return only the JSON and nothing else


You can use the following example for getting help:

Input action description:
Type "shoes" in the search bar and click the search button

Input xpath dictionary:
{{
  "hamburger menu" : <ham-xpath-1>,
  "cart button" : <cart-button-1>,
  "orders menu" : <order-menu-1>,
  "account information menu" : <acc-info-1>,
  "kids" : <kids-menu-1>,
  "women" : <women-menu-1>,
  "men" : <men-menu-1>,
  "footwear" : <footwear-menu-1>,
  "hover-menu-1" : <hover-menu-1-xpath>,
  "search" : <search-xpath-1>,
  "search input" : <search-input-xpath-1>,
  "search-button" : <search-button-xpath>,
  "login-menu" : <login-menu-xpath>,
  "sign-up" : <sign-up-xpath>,
  "offer-on-shoes-40-off" : <xpath-123>,
  "offer-on-women-clothing" : <xpath-383>,
  "offer-on-art-craft-40-off" : <xpath-545>,
  "saved-addresses" : <saved-addresses-xpath-1>
}}

For the above inputs the output must be the following: 
{{
    "search-input" : <search-input-xpath-1>,
    "search-button" : <search-button-xpath>
}}

The following is the justification for the output (this will not be the part of the output):
1. for typing in something "search-input" is picked up out of all elements
2. for clicking the button "search-button" is picked out of all elements
3. out of "search" and "search-input", "search-input" is picked as it infers more for typing in something
4. "offer-on-shoes-40-off" has not been picked as it "shoes" is just an input for "search-input" 
"""