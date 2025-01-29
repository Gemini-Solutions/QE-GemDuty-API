import re
import json

json_string = """
Here is the extracted information in JSON format:{
  "feature": [
    {"name": "Flash Messages", "description": "Displays flash messages", "xpath": "//div[@id='flash-messages']"},
    {"name": "GitHub Link", "description": "Displays a link to GitHub", "xpath": "//a[@href='https://github.com/tourdedave/the-internet']"},
    {"name": "Fork Me Image", "description": "Displays a fork me image", "xpath": "//img[@alt='Fork me on GitHub']"},
    {"name": "Content Section", "description": "Displays the main content section", "xpath": "//div[@id='content']"},
    {"name": "Broken Images", "description": "Displays broken images", "xpath": "//div[@class='example']//img"},
    {"name": "Page Footer", "description": "Displays the page footer", "xpath": "//div[@id='page-footer']"},
    {"name": "Elemental Selenium Link", "description": "Displays a link to Elemental Selenium", "xpath": "//a[@href='http://elementalselenium.com/']"}
  ]
}

Note: I've identified the following features based on the provided HTML code:

1. Flash Messages: The div with id "flash-messages" is expected to display flash messages.
2. GitHub Link: The link with href "https://github.com/tourdedave/the-internet" is expected to be displayed.
3. Fork Me Image: The img with alt "Fork me on GitHub" is expected to be displayed.
4. Content Section: The div with id "content" is expected to display the main content section.
5. Broken Images: The div with class "example" is expected to display broken images.
6. Page Footer: The div with id "page-footer" is expected to display the page footer.
7. Elemental Selenium Link: The link with href "http://elementalselenium.com/" is expected to be displayed.

I've created valid XPath expressions for each feature based on the HTML code.
"""


# Example dynamic string containing JSON

# Use regex to find JSON objects (assuming the JSON object starts with '{' and ends with '}')
json_match = re.search(r"\{.*\}", json_string, re.DOTALL)

if json_match:
    json_str = json_match.group()
    # Parse the extracted JSON string into a Python dictionary
    data = json.loads(json_str)
    print(data)
else:
    print("No JSON found in the string.")
