import os
import re
import json
import yaml
import requests
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from functions.make_chunks_of_swagger_json import divide_swagger_json_by_tag_and_method
from utils.llm_call import call_anthropic_model
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from threading import Lock


search_terms = ["api-docs", "swagger.json", "openapi.json", "swagger.yaml"]

global_function_definitions = {}
method_occurrences = {}
java_content_dict = {}

# TODO : move to prompts - separate file
BDD_PROMPT = """
You will be given a JSON input. Your goal is to generate a Cucumber Java Gherkin Feature file and a corresponding Java Step Definition file that follows that utilizes the Cucumber.
The JSON is provided between the markers ---INPUT-JSON-START---- and ---INPUT-JSON-END----. This JSON describes endpoints, operations, tags, parameters, request bodies, and possible responses. You will rely solely on the contents of this JSON—no assumptions or additions outside of it.

---INPUT-JSON-START----
{input_json}
---INPUT-JSON-END----

Use the following general instructions for Generating the required files
1. Carefully parse the JSON to gather endpoint paths, HTTP methods, parameters (including path, query, and body parameters), possible status codes, and the associated schemas for requests and responses.
2. The Class name in the step definition file should be {class_name}
3. Determine which fields are enums, which are required fields, and which can have dummy data.
4. Note any constraints (string patterns, number ranges, length constraints, etc.).

Use the following general instructions for Generating the Feature File
1. Go through the input JSON and find out all the endpoints mentioned in the JSON
2. Create a Background section to set up any required steps (e.g., base URL, authorization token).
3. Write Scenario Outline blocks for Valid input scenario and invalid input scenario(violating the constraints), Missing required fields scenarios, Response codes scenarios (200, 400, 401, 404, etc.) as indicated by the JSON.
4. If the endpoint has query parameters, then examples are supposed to be mentioned in feature files
5. If examples are present then the Scenario section must be named as `Scenario Outline` else it should be named as `Scenario`
6. Use the tag names as prefixes to the steps in the Scenario outlines.
7. Include placeholders (like <variable>) in the steps, and pass them via an Examples table.
8. Ensure that all the endpoints are covered in the Feature file. 

Use the following general instructions for generating the Step Definition File
1. Go through the input JSON and find out all the endpoints mentioned in the JSON
2. Create a Java class (same as the feature file name) inside a stepdefinitions package with package name as {step_def_package_name}
3. generate the code for implementing endpoints as mentioned in the Feature file, including the steps in Background section.
4. for each step mention the data type of the sample data in the annotations as per the following rule - it should be be `int` for whole numbers, `string` for series of characters, `float` for decimal numbers, example the step "the user is on the home page" should be @Given("the user is on the home page {{string}}")
5. Use methods from a SerenityRest library to perform requests (GET, POST, DELETE, etc.) and to validate responses.
6. Ensure each placeholder from the Feature file is properly handled and passed to the request/response logic.
7. Examine the JSON input for each API endpoint to detect the presence of a security field. This field indicates if the endpoint requires authentication.
8. For endpoints with a security field, include steps in your step definition files to verify the validity of authentication tokens or API keys as specified in the JSON.
9. For endpoints lacking a security field, generate standard step definitions that proceed without implementing authentication checks, maintaining clarity and compliance with security protocols.
10. Include assertions for the response status code and any relevant response body content or schema validations.
11. Do not leave any method empty or with placeholder comments—provide a complete implementation.
12. For path parameters (e.g., {{petId}}), convert them into Gherkin placeholders (e.g., <petId>) and ensure Step Definitions pass the dynamic value correctly in the request URL.
13. If the JSON marks an endpoint as deprecated, specify whether to skip generating tests or add a clear note that the endpoint is deprecated.
14. Ensure that generated code should have validation for all status codes mentioned in the input JSON

Important Instructions
1. Swagger-Only Scope: Do not go beyond what the JSON defines.
2. Ensure that the class name, step definition file name, feature name, and feature file name all match the Swagger tag.
3. Avoid Redundancy: Each scenario should be unique.
4. Strict Accuracy: Follow the JSON exactly—no inferred or extra details.
5. Use simple syntax (e.g., SerenityRest or similar HTTP library calls).
6. No extraneous placeholders or references to methods like useBaseUrl or setBaseUrl.

Use the following general instructions for Data Generation for the fields:
1. For required fields, use placeholders that the user can supply at runtime.
2. For enum fields, add a comment listing possible values next to the placeholder.
3. For non-required fields, generate dummy values that comply with the constraints.
4. Assertions: Check for correct status codes and error messages where needed.

Example Input:
Feature file
Feature: Pet
As a user
I want to interact with the Pet API
Background:
Given the base URL is "https://petstore.swagger.io/v2"
And the authorization token is "<authToken>"  # e.g., "special-key"
Scenario Outline: Add a new pet with valid input
When I send a POST request to "/pet" with body:
"""
{
"id": "<petId>",
"name": "<petName>",
"status": "<petStatus>" # Possible values: ["available","pending","sold"]
}
"""
Then the response status code should be 200
And the response body should contain the pet id

Examples:
    | authToken    | petId | petName   | petStatus   |
    | special-key  | 100   | TestPet   | available   |

Scenario Outline: Add a new pet with invalid input
When I send a POST request to "/pet" with body:
"""
{
"id": "<petId>",
"name": "<petName>" # status is missing here
}
"""
Then the response status code should be 400
And the response body should contain an error message
Examples:
    | authToken   | petId | petName |
    | special-key | 101   | InvalPet |
Step definition
package stepdefinitions;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.When;
import io.cucumber.java.en.Then;
import net.serenitybdd.rest.SerenityRest;
import org.junit.Assert;
public class PetStepDefinitions {
    @Given("the base URL is {string}")
    public void setBaseUrl(String baseUrl) {
        SerenityRest.setDefaultBasePath("");
        SerenityRest.given().baseUri(baseUrl);
    }
    @When("I send a POST request to {string} with body:")
    public void sendPostRequest(String path, String body) {
        SerenityRest.given()
            .contentType("application/json")
            .body(body)
            .when()
            .post(path);
    }
    @Then("the response status code should be {int}")
    public void theResponseStatusCodeShouldBe(int statusCode) {
        int actualStatusCode = SerenityRest.then().extract().statusCode();
        Assert.assertEquals("Incorrect status code", statusCode, actualStatusCode);
    }
    @Then("the response body should contain the pet id")
    public void theResponseBodyShouldContainThePetId() {
        String responseBody = SerenityRest.then().extract().body().asString();
        Assert.assertTrue("Pet id not present", responseBody.contains("id"));
    }
    @Then("the response body should contain an error message")
    public void theResponseBodyShouldContainAnErrorMessage() {
        String responseBody = SerenityRest.then().extract().body().asString();
        Assert.assertTrue("Error message is not present in the response body",
                responseBody.contains("error") || responseBody.contains("Error"));
    }
}
Justification of the Example Output:
Feature File: Illustrates how each scenario is derived from the Swagger JSON specification, focusing on valid and invalid inputs and the corresponding response codes.
Step Definitions: Show how each Gherkin step is implemented with actual code, demonstrating calls to SerenityRest for HTTP operations, plus verification logic for status codes and response content.
"""


lock = Lock()

async def launch_UI(url):
    print("Inside launch")
    async with async_playwright() as p:
        print("Inside Playwright")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        api_docs_url = await find_api_docs_url(page, url)
        await browser.close()
        return api_docs_url


def handle_request(request, api_docs_url):
    if request.resource_type in ["xhr", "fetch"]:
        for term in search_terms:
            if request.url.endswith(term):
                api_docs_url[0] = request.url
                break
    return api_docs_url


async def find_api_docs_url(page, url):
    api_docs_url = [None]
    page.on("request", lambda request: handle_request(request, api_docs_url))

    try:
        await page.goto(url)  # Navigate to the target page
        await page.wait_for_timeout(20000)  # Wait for 20 seconds to capture requests
    except Exception as e:
        print(f"Error: {e}")

    return api_docs_url[0]


def validate_type_of_request(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        content_type = response.headers.get("Content-Type", "").lower()
        if content_type in ["application/json", "application/xml", "application/yaml"]:
            return "API"
        elif "text/html" in content_type:
            return "UI"
        else:
            return "Invalid"
    except requests.RequestException as e:
        return f"Error: Failed to fetch {url}. Due to {str(e)}"


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


MAX_WORKERS = 5

step_definition_template = """
import cucumber.api.java.en.When;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;
import org.junit.Assert;

public class PetSteps {{
    {step_definition_string}
}}
"""


# function for changing the tag name to standard naming convention
def clean_and_capitalize(string):
    """
    Removes special characters and capitalizes the first letter of each word
    in the string, treating separators like hyphens as word boundaries.

    Args:
        string (str): The input string containing special characters and separators.

    Returns:
        str: The cleaned and capitalized string.
    """
    # Remove special characters except alphanumeric
    cleaned_string = re.sub(r'[^a-zA-Z0-9]', ' ', string)
    
    # Split by whitespace, capitalize each word, and join without spaces
    words = cleaned_string.split()
    capitalized_words = [word.capitalize() for word in words]

    # Join words back into a single string without spaces
    return ''.join(capitalized_words)



def process_chunk(chunk, prompt_, tag_name, method_name, content_queue):
    try:
        tag_name = clean_and_capitalize(tag_name)
        file_name = f"{tag_name}{method_name.capitalize()}"
        step_def_package_name = f"stepdefinitions.{tag_name}.{method_name}"
        prompt = prompt_.format(input_json=chunk,class_name=file_name, step_def_package_name=step_def_package_name)
        try:
            content = call_anthropic_model(prompt)
        except Exception as e:
            print(f"Error calling AWS Bedrock LLM: {e}")
            return

        gherkin_content = extract_code_block(content, 'gherkin')
        java_content = extract_code_block(content, 'java')

        feature_name = file_name
        if feature_name and gherkin_content:
            gherkin_filename = f"generated_code/features/{tag_name}/{method_name}/{file_name}.feature"
            write_to_file(gherkin_filename, gherkin_content, "feature")

        if java_content:
            java_filename = f"generated_code/stepdefinitions/{tag_name}/{method_name}/{(file_name)}.java"
            java_content = process_java_content(java_content)
            write_to_file(java_filename, java_content, "java")

        # Add content to the queue for merging later
        # content_queue.put(java_content)

    except Exception as e:
        print(f"Error processing chunk: {e}")


def trigger_iam_user(chunks):
    prompt_ = BDD_PROMPT
    # prompt_cleanup = cleanup_prompt
    content_queue = Queue()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for tag_name, method_chunk in chunks.items():
            for method_name, chunk in method_chunk.items():
                executor.submit(process_chunk, chunk, prompt_, tag_name, method_name, content_queue)
    # merge_string = "" # TODO : CAN WE REMOVE THIS ?
    # while not content_queue.empty():
    #     merge_string += content_queue.get()
    # step_definition_string = step_definition_template.format(step_definition_string=merge_string)
    # print(step_definition_string)
    # prompt = prompt_cleanup.format(content=step_definition_string)
    # content = call_aws_bedrock_llm(prompt)
    # java_content = extract_code_block(content, "java")
    # java_filename = "generated_code/step_definitions/UnifiedSteps.java"
    # write_to_file(java_filename, java_content, "java")

# TODO : move this to general_utils 
def extract_code_block(content, language):
    start_marker = f"```{language}"
    start = content.find(start_marker)
    if start != -1:
        start += len(start_marker)
        end = content.find("```", start)
        return content[start:end].strip()
    return None


def extract_feature_name(gherkin_content):
    if gherkin_content:
        match = re.search(r"Feature:\s*(.*)", gherkin_content)
        if match:
            feature_name = match.group(1).strip()
            # Remove special characters and replace spaces with underscores
            return re.sub(r"[^a-zA-Z0-9]", "", feature_name)
    return None


def extract_function_name(java_content):
    if java_content:
        match = re.search(r"\s+public\s+void\s+(\w+)\s*\(", java_content)
        if match:
            return match.group(1).strip()
    return None


def write_to_file(filename, content, file_type):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            file.write(content)
        print(f"{file_type.capitalize()} content written to {filename}")
    except Exception as e:
        print(f"Error while writing {file_type} file: {e}")


def given_input_is_url_address(input_string):
    try:
        result = urlparse(input_string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# TODO : move to api_utils
def traverse_collection(pm_collection):
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

# TODO : move to general_utils
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

# TODO : move to 

def process_chunks_to_list(chunks):
    ans_dict = {}
    for tag_name, method_chunk in chunks.items():
        ans_dict[tag_name] = list(method_chunk.keys())
    
    return ans_dict

async def process_selected_chunks(original, selected):
    
    ans_dict = {}
    
    for tag_name, method_list in selected.items():
        
        for method in method_list:
            if tag_name in original and method in original[tag_name]:
                if tag_name not in ans_dict:
                    ans_dict[tag_name] = {}
                ans_dict[tag_name][method] = original[tag_name][method]
    trigger_iam_user(chunks=ans_dict)
    
async def is_swagger_ui_url(user_input):
    urls = await launch_UI(user_input)
    if urls is None or urls == "":
        print("No Swagger Documentation API found in Swagger UI network tab")
        return {}
    data = fetch_and_validate_api(urls)
    if not data:
        print("Data not found")
        return {}
    chunks = divide_swagger_json_by_tag_and_method(data)
    return chunks


def is_file_path_or_postman_collection(user_input):
    data = input_is_file_path_and_data_is_of_postman_collection(user_input)
    if data:
        chunks = traverse_collection(data)
        trigger_iam_user(chunks)
    else:
        print("postman collection data is invalid")


def process_java_content(java_content):
    step_pattern = r"(@[^\s]+\s*\([^\)]*\))\s*(public|private|protected|default)?\s+\w+\s+\w+\s*\([^)]*\)\s*\{[\s\S]*?\}\s*\n\s*\n"

    updated_content = java_content
    matches = re.finditer(step_pattern, java_content, re.DOTALL)

    for match in matches:
        full_step_definition = match.group(0)  # Full match (annotation + method body)
        step_annotation = match.group(1)  # The annotation part
        annotation_string_match = re.search(r'\"([^\"]+)\"', step_annotation)
        
        if annotation_string_match:
            annotation_string = annotation_string_match.group(1)
            if annotation_string in method_occurrences:
                global_function_definitions[annotation_string] = full_step_definition
            else:
                method_occurrences[annotation_string] = full_step_definition
    for annotation_string, full_step_definition in global_function_definitions.items():
        commented_body = f"/* {full_step_definition} */"
        updated_content = updated_content.replace(full_step_definition, commented_body)
    
    return updated_content
