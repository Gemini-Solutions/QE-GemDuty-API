ROUTER_PROMPT = """
You will be given a piece of text and input which can be either a greeting message or sophisticated set of instructions to perform an action on a webpage.
Your task is to classify the text either as `greetings` or `sophisticated instructions` and also mention what was the input text missing from being a `sophisticated instruction`, you need to return a JSON which will have the following schema:
{{
    "classified_type" : <classification type>,
    "missing_params" : <parameters missing from input text for being a `sophisticated instruction`>
}} 

the following is the piece of text between `---TEXT-START---` and `---TEXT-END---`
---TEXT-START---
{input_text}
---TEXT-END---

You can use the following points to complete the classification task:
1. The input text can be classified as `sophisticated instruction` only if it contains actions to be done on a webpage of a website and URLs on which the user gets redirected while the instructions are performed on the website, for this kind of the instructions the attribute `missing_params` will be assigned as `NULL`. (some exceptional cases may have only one URL along with required instructions to be performed on the webpage then also classify it as `sophisticated instructions`, with `missing_params` as NULL).   
2. The input text will be classified as `greeting` if the given text is none of the above or appears to be like a greeting or a message which is not like an instruction or just a simple query about anything out of context. The `missing_params` attribute will have the value `ALL` as it does not have anything related to a `sophisticated instruction` type of input text, use the same logic to classify the input text as `greeting`.

Important instructions:
1. return only the JSON as the described schema and nothing else

You can use the following example for performing this classification task:

Input text:
Background: User login at https://mymis.geminisolutions.com/Account/Login
User Types user id : 'webadmin'
User types password : 'Gemini@1234' and logs in
redirect to : https://mymis.geminisolutions.com/
Scenario Outline: Test for adding new asset type on Mymis
User navigates to manage assets under Asset Allocation
redirect to : https://mymis.geminisolutions.com/Asset/Manage⁠
User clicks on Add new asset type
User gives asset type as "testing123" and Selects yes for Is temporary option and adds it 

output JSON:
{{
    "classified_type" : "sophisticated instructions",
    "missing_params" : "NULL"
}} 
Justification:
1. The input text contains both the actions to be performed on the webpages as well as the URLs on which the user will get redirected when action is performed on it.

Input Text: 
Go to https://www.amazon.in
search for `shoes`
redirect to : `https://www.amazon.in/query?keyword=shoes`    
click on the first search result
redirect to : `https://www.amazon.in/query?keyword=shoes/result_id=110101`
click on Add to cart and confirm the message `Item added to cart`        

output JSON:
{{
    "classified_type" : "sophisticated instructions",
    "missing_params" : NULL
}} 

Justification:
1. The input text contains both the actions to be performed on the webpages as well as the URLs on which the user will get redirected when action is performed on it.

Input text:
Hi, my name is Andrew, how are you? 
OR
Hi how are you doing ?
OR
What did the elephant have for the dinner ? 
OR 
whats the percentage of test cases real ?

output JSON:
{{
    "classified_type" : "greeting",
    "missing_params" : "ALL" 
}} 

Justification:
1. the input texts mentioned are either a greeting or a vague questions or a question which is not an instruction which has the properties of a `sophisticated instruction` as it does not have the action or the redirection URLs.  
"""