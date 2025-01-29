from urllib.parse import urlparse
import requests
import uuid
from playwright.sync_api import sync_playwright
import json
import yaml
import os
from functions.make_chunks_of_swagger_json import divide_swagger_json
from utils.llm import call_aws_bedrock_llm
import re

# TODO : move to ./prompts 
TDD_PROMPT = """
Objective: Generate comprehensive Rest Assured test cases based on the provided Swagger JSON, covering all significant positive and negative scenarios as defined in the Swagger specification.Exclude any extra text, introductory lines, or explanations outside of the ```java code block.

Instructions:
Swagger-Only Scope: Do not include features and functionalities that are not defined in the Swagger JSON. Avoid making assumptions or adding details not present.
Unique Test Cases: Ensure each test case is unique and avoids redundancy.
Strict Accuracy: Adhere strictly to the provided Swagger JSON without inferring or adding additional details.
Data Generation:
Identify Fields for User Input: Determine which fields and parameters in the request body, headers, and query parameters must be provided by the user. Use placeholder variables for these fields in the generated code, with comments indicating that the user must supply these values at runtime. Example: Authorization token,Bearer Token, username etc.
Handle Enum Fields: For fields defined with enum values in the Swagger JSON add a comment next to the placeholder variable listing all possible enum values that the user can choose from when supplying input. Example: // Possible values: ["value1", "value2", "value3"]
Generate Dummy Data: For fields where user input is not required, generate appropriate dummy data that strictly adheres to the schemas and constraints defined in the Swagger JSON. Ensure dummy values comply with constraints such as string patterns, numerical ranges, data types and examples. Ensure that integer fields are not mistakenly stored in string variables.
Test Case Coverage:
Valid Inputs: Test cases with inputs that match the Swagger schema.
Invalid Inputs: Test cases with inputs that violate schema constraints.
Missing Fields: Cases where required fields are missing.
Response Status Codes: Cases covering different status codes based on input variations.
Code Requirements:
No Extra Code: Do not create or use additional classes (e.g., TestExeDto). Construct request bodies using JSON strings directly within the test cases.
Host URL Inclusion: Include the host URL as a user-provided parameter with clear comments indicating where the user should supply this value.
Assertions: Include appropriate assertions for validating responses, such as status codes, response bodies, and headers.
Code Clarity: Ensure that the test cases are straightforward and directly correspond to the specifications in the Swagger JSON.
Input: {input_json}

Output: Provide the Rest Assured test cases in Java code format, structured to cover the defined Swagger operations with all required scenarios.
"""
# TODO :  move to ./prompts
BDD_PROMPT = """
Objective: Generate comprehensive Cucumber java Gherkin feature files and corresponding step definition files for functional test cases based on the provided JSON, covering all significant positive and negative scenarios as defined in the JSON.Exclude any extra text, introductory lines, or explanations outside of the ```java code and ```gherkin block.
Instructions:
Swagger-Only Scope:
Do not include features and functionalities that are not defined in the JSON.
Avoid making assumptions or adding details not present in the JSON.
Unique Test Cases:
Ensure each test case is unique and avoids redundancy.
Strict Accuracy:
Adhere strictly to the provided JSON without inferring or adding additional details.
Data Generation:
Identify Fields for User Input:
Determine which fields and parameters in the request body, headers, and query parameters must be provided by the user.
Use placeholder variables for these fields in the generated Gherkin scenarios, with comments indicating that the user must supply these values at runtime.
Example: Authorization token, Bearer Token, username, etc.
Handle Enum Fields:
For fields defined with enum values in the JSON, add a comment next to the placeholder variable listing all possible enum values that the user can choose from when supplying input.
Example: // Possible values: ["value1", "value2", "value3"]
Generate Dummy Data:
For fields where user input is not required, generate appropriate dummy data that adheres to the schemas and constraints defined in the JSON.
Ensure dummy values comply with constraints such as string patterns, numerical ranges, data types, and examples.
Host URL Inclusion:
Include the host URL as a user-provided parameter with clear comments indicating where the user should supply this value.
Assertions:
Include appropriate assertions in the step definitions for validating responses, such as status codes, fields of response bodies, and headers.
Test Case Coverage:
Valid Inputs:
Gherkin scenarios with inputs that match the schema defined in JSON.
Invalid Inputs:
Gherkin scenarios with inputs that violate schema constraints.
Missing Fields:
Gherkin scenarios where required fields are missing.
Response Status Codes:
Gherkin scenarios covering different status codes based on input variations.
Input: {input_json}

Output:
Gherkin Feature File:
A Gherkin feature file containing scenarios, background and steps based on the JSON.
The request body should be passed correctly from the Gherkin file to the step definition using placeholders.
Step Definition Files:
A corresponding set of step definition files with implementation for the scenarios in the Gherkin feature file.
Implement actual logic in the step definition file.
"""


def launch_UI(url):
    with sync_playwright() as p:
        page = p.chromium.launch(headless=True).new_page()
        api_docs_url = find_api_docs_url(page, url)
        page.context.browser.close()
        return api_docs_url


def find_api_docs_url(page, url):
    api_docs_url = None
    search_terms = ["api-docs", "swagger.json", "openapi.json", "swagger.yaml"]

    def handle_request(request):
        nonlocal api_docs_url
        if request.resource_type in ["xhr", "fetch"]:
            for term in search_terms:
                if term in request.url:
                    api_docs_url = request.url
                    break

    page.on("request", handle_request)
    page.goto(url)
    page.wait_for_timeout(3000)
    return api_docs_url


def given_input_is_swagger_Api(url: str) -> str:
    response = requests.get(url, timeout=10)
    content_type = response.headers.get("Content-Type", "").lower()
    if (
        "application/json" in content_type
        or "application/xml" in content_type
        or "application/yaml" in content_type
    ):
        return "API"
    elif "text/html" in content_type:
        return "UI"
    else:
        return "Invalid"


def fetch_and_validate_api(url):
    try:
        # Trigger the API and get the response
        response = requests.get(url)

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        # Try to parse the response as JSON
        try:
            data = response.json()
        except json.JSONDecodeError:
            # If JSON decoding fails, try parsing as YAML
            try:
                data = yaml.safe_load(response.text)
                # Convert YAML data to JSON by converting Python object to JSON string
                data = json.loads(json.dumps(data))
            except yaml.YAMLError:
                return None

        # Check if "openapi" or "swagger" key is present
        if "openapi" in data or "swagger" in data:
            return data  # Always return the data in JSON format
        else:
            return None

    except requests.RequestException as e:
        print(f"Error fetching API: {e}")
    except KeyError as e:
        print(f"Exception: {e}")


def triggerIAMUser(chunks, testcase_type):
    # fileName = "./outputFolder/output__"+str(uuid.uuid4())+".txt"
    if testcase_type == "TDD":
        prompt_ = TDD_PROMPT
    else:
        prompt_ = BDD_PROMPT

    for i, chunk in enumerate(chunks):
        prompt = prompt_.format(input_json=chunk)
        content = call_aws_bedrock_llm(prompt)
        start_gherkin = content.find("```gherkin")
        gherkin_content = None
        if start_gherkin != -1:
            start_gherkin += len("```gherkin")
            end_gherkin = content.find("```", start_gherkin)
            gherkin_content = content[start_gherkin:end_gherkin].strip()

        # Extract Java content
        start_java = content.find("```java")
        java_content = None
        if start_java != -1:
            start_java += len("```java")
            end_java = content.find("```", start_java)
            java_content = content[start_java:end_java]

        # Extract feature name from Gherkin content using regex (if Gherkin exists)
        feature_name = None
        if gherkin_content:
            match = re.search(r"So that I can\s*(.*)", gherkin_content)
            if match:
                feature_name = match.group(1).strip()
                # Remove special characters and replace spaces with underscores
                feature_name = re.sub(r"[^a-zA-Z0-9]", "", feature_name)
            else:
                raise ValueError("Feature name not found in the Gherkin content")

        # If no feature name, extract Java function name for the Java file name
        function_name = None
        if not feature_name and java_content:
            match = re.search(r"\s+public\s+void\s+(\w+)\s*\(", java_content)
            if match:
                function_name = match.group(1).strip()

        # Write Gherkin content to .feature file (only if Gherkin content exists)
        if feature_name:
            os.makedirs("features", exist_ok=True)
            gherkin_filename = f"features/{feature_name}.feature"
            with open(gherkin_filename, "w") as feature_file:
                feature_file.write(gherkin_content)
            print(f"Gherkin content written to {gherkin_filename}")
            os.makedirs("step_definitions", exist_ok=True)
            java_filename = f"step_definitions/{feature_name}Steps.java"
        else:
            os.makedirs("TDD_Testcases", exist_ok=True)
            java_filename = f"TDD_Testcases/{function_name}Steps.java"

        # Write Java content to .java file (always create Java file if Java content exists)
        if java_content:
            with open(java_filename, "w") as java_file:
                java_file.write(java_content)
            print(f"Java content written to {java_filename}")

# TODO : check for duplicate - move to general_utils
def given_input_is_url_address(input_string):
    try:
        result = urlparse(input_string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def traverse_collection_iterative(pm_collection):
    exported_endpoints_list = []
    stack = [pm_collection]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            if "item" in current:
                stack.append(current["item"])
            else:
                testcase = {}
                for key, value in current.items():
                    if (
                        key == "name"
                        or key == "request"
                        or key == "url"
                        or key == "response"
                    ):
                        testcase[key] = value
                exported_endpoints_list.append(testcase)
        elif isinstance(current, list):
            stack.extend(current)
    return exported_endpoints_list


def input_is_file_path_and_data_is_of_postman_collection(file_path):
    try:
        # Read the file content
        with open(file_path, "r") as file:
            file_content = file.read()

        # Attempt to load the file content as JSON
        try:
            data = json.loads(file_content)
        except json.JSONDecodeError:
            # If JSON decoding fails, try YAML
            try:
                data = yaml.safe_load(file_content)
                # Convert YAML to JSON
                data = json.dumps(data)
            except yaml.YAMLError:
                return False

        # Check if 'info' key exists in the JSON data
        try:
            if "info" in data and "_postman_id" in data["info"]:
                return data
            else:
                return False
        except (json.JSONDecodeError, TypeError):
            return False

    except Exception:
        return False

# TODO : find duplicate - move to general_utils
def given_input_is_valid_file_path(path):
    # Check if the path exists and is a file
    if os.path.isfile(path):
        # Check if the file is not empty
        if os.path.getsize(path) > 0:
            return True
        else:
            return False
    else:
        return False


def commitOperationIfInputIsSwaggerUiUrl(user_input, testcase_type):
    urls = launch_UI(user_input)
    if urls == None or urls == "":
        print("No Swagger Documentation api found in swagger UI network tab")
    data = fetch_and_validate_api(urls)
    if data is []:
        print("data not found")
    chunks = divide_swagger_json(data)
    triggerIAMUser(chunks=chunks, testcase_type=testcase_type)


def commitOperationIfInputIsSwaggerApiUrl(user_input, testcase_type):
    data = fetch_and_validate_api(user_input)
    if data is []:
        print("data not found")
    chunks = divide_swagger_json(data)
    triggerIAMUser(chunks=chunks, testcase_type=testcase_type)


def commitOperationIfInputIsFilePathOrPostmanCollection(user_input, testcase_type):
    data = input_is_file_path_and_data_is_of_postman_collection(user_input)
    if data:
        chunks = traverse_collection_iterative(data)
        triggerIAMUser(chunks, testcase_type)
    else:
        print("postman collection data is invalid")
