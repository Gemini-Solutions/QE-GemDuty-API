
ACTION_REDIRECTION_LINK = """
You will be given a set of instructions as an input, these are the instructions directing to perform an action on a website, the instructions follow a pattern of performing action on webpage and then getting redirected to another page after performing a certain action on the webpage, along with this the instructions shall also contain the url of the landing page and urls of the all the pages to which we are redirected to.

Your task is to identify and segregate the actions performed on webpage and the URL responsible for redirecting from that webpage to another, return the 
extracted action against URL AS JSON, with action performed against URL of the webpage.


The followings is the task description given between separators `---TASK-DESCRIPTION---` and `---TASK-DESCRIPTION---`
---TASK-DESCRIPTION---
{task_description}
---TASK-DESCRIPTION---

You need to follow the below instructions for completing the task:
1. First go through the task description and understand where all redirection is taking place, in the task description it is specifically mentioned when and where the redirection is taking place.
2. Identify the actions taking on different webpages, you can segregate the actions taking place on different webpages by keeping a note of actions taking place before every redirection
3. The Task description may also contain variables enclosed between < and > and they value will be given in the Example Section of the task description, replace the place-holders / variable in the task description with the values present in the Example section. 
4. While specifying the actions precisely include the action (eg- clicked, typed etc) and the name of the element in which action is performed (eg- button name, search bar name etc).
5. If the action is of filing values in some fields whose placeholders are given as `<placeholder-name>`, then the action must be described as `user types <value> in "placeholder-name"` for each place-holder, the value will be available in the Example section of the task description.
6. If the place-holder is the `file-path` or `file-name`  the the action would be to browse the given file and add it, the value of place-holder will be given in the example section of task description
7. classify the action as  `Login` or `No-Login`, this will be based on fact if the action of authentication or logging in to website is being done or not, if there is an action of logging in then assign it as `Login` else assign `No-Login` 
8. The keywords mentioned in between the brackets < and > are variables keep them as it is while specifying in actions. 
9. Once the actions and the URLs are identified, then arrange the webpage actions against the URLs for that webpage

Assume some actions to be obvious which may be the following:
1. When action is search then next step would be to press enter
2. When action is adding the new entry then final step would be clicking a final add button
3. When some item is to be selected from a dropdown first click on the dropdown 
4. When action is of putting the credentials then first step is to type the login id / email id and then type password in input fields and then click on login or sign in.
5. When date range is to be selected and a range is given eg: "18th-20th of the current month" then selecting 18th day of the current month as "Event from" date as first step  and 20th day of the current month as "Event till" date as the second step, where would be as per the context of the task description, it might be check-in / check-out or leave from / leave to.
6. When there are words like `before` and `after` given then consider them for deciding the order of the steps
7. When the action is Confirm to something it will refer to clicking on a "yes" button or some button having an equivalent name
8. When the action refers to adding something infer it as clicking "Add <item>" button where item should be inferred from the action
9. When the action is export then it refers to clicking "Export" or "Download" button
10. When the action is of select then it refers to clicking the dropdown and then clicking on the option as specified in the task
11. When the action is checks or toggles it will refer to checking the check box for selecting the respective value

Important Instructions:
1. The actions must be mapped to the webpage URL on which the actions are taking place
2. Add the Assumed action to the webpage action key for stream lining the process.
3. Return only JSON and nothing else, the json will have the following format
{{
    <webpage-actions-1> : {{"action_type" : <Login or No-Login>  , "url" : <URL-of-webpage-1>}},
    <webpage-actions-2> : {{"action_type" : <Login or No-Login>  , "url" : <URL-of-webpage-2>}}
}}   

You can use the following example for understanding the same:

input task description:

Scenario Outline: Testing Manage Access Card at Search functionality at https://mymis.geminisolutions.com
When user navigates on "Access Card Management" and then "Manage Access Card"
User gets redirected to "Manage Access Card" page at https://mymis.geminisolutions.com/AccessCard/Manage
And searching a "<Card Number>"card by typing "<Card Number>" in the search input
Then Verify search function is "<Card Number>" working
Examples:
| Card Number |
| 125552356   |


The JSON output to be returned will be
{{
    "Navigation to `Access Card Management` and then click `Manage access card`" : "https://mymis.geminisolutions.com"
    "search by Typing `<Card Number>` as search input" : "https://mymis.geminisolutions.com/AccessCard/Manage"
}}
"""


VARIABLE_NAME_REPLACE_PROMPT = """
You will be given a base JSON which will contain variables enclosed between `<` and `>`, along with this you will be given a task description along with the table which contains the values of the variable.
Your task is to extend the JSON such that the variables are replaced values mentioned in the table of the initial description. Extend the JSON as a list of JSONs and return me the list of JSONs in which each JSON corresponds to the variable replaced with actual value for all the values in the table.

the Following is the task description given between `---DESCRIPTION-START---` and `---DESCRIPTION-END---`

---DESCRIPTION-START---
{task_description}
---DESCRIPTION-END---

the following is the JSON given between `---JSON-START---` and `---JSON-END---`

---JSON-START---
{json}
---JSON-END---

You must use the follow the below instructions in order to complete the given task:
1. the task description must be ignored and the table containing the values must be considered
2. only the variables must be replaced with the values given in the table
3. If more than 1 JSON is being formed then return a list of JSONs containing variables replaced by values form tables
4. If no table is present in the description then return the JSON as it is.

Important instructions
1. Return only the List of JSONs and nothing else
"""
