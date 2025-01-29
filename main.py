import re
import streamlit as st
import pandas as pd
import zipfile
import json
import os
import asyncio
import sys
import time


from utils.api_util import (
    validate_type_of_request,
    is_swagger_ui_url,
    traverse_collection,
    trigger_iam_user,
    process_chunks_to_list,
    process_selected_chunks
)

from utils.user_story_parser import generate_testcases_from_user_story_or_description

from functions.feature_finder import st_scrape_and_extract_features
from functions.code_block_summarizer import st_summarizer_function

from utils.extract_codeblock_from_xpath import extract_code_block
from functions.test_generation import (
    st_create_initial_test_case,
    st_create_additional_test_case,
)

from functions.code_generation import st_generate_code
from utils.fetch_scenarios_list import (
    fetch_scenarios_list,
    generate_string_from_scenario,
    fetch_feature_header,
)
from utils.feature_file_code_generation import generate_test_cases_feature_file
from utils.json_to_gherkin import parse_assistant_output
from utils.user_story_regneration import regenerate_as_per_instructions
from utils.general_utils import read_all_files
# Add option to select the LLM model to generate test cases
# llm_options = ["ChatGPT (Leaving soon)", "Llama", "Claude"]
# selected_option = st.radio(
#     "Choose a LLM model to generate the test cases: ", llm_options, index=1
# )



# session state to prevent code to re-run while
if 'dir_names' not in st.session_state:
    st.session_state.dir_names = []

selected_option = "Claude"
time_keeper = []

def remove_dir(folder_path):
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    for root, dirs, files in os.walk(folder_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
            print(f"Deleted file: {file_path}")

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            os.rmdir(dir_path)
            print(f"Deleted directory: {dir_path}")
    os.rmdir(folder_path)


def stop_api_rerun():
    if "downloaded" not in st.session_state:
        st.session_state.downloaded = False

    if not st.session_state.downloaded:
        if input_method in ["Postman Collection", "Swagger Url"]:
            st.markdown("## Testcase Generation Summary")
            st.text_area("Generated Summary", "Your testcases have been generated")

            try:
                if os.path.isdir("./generated_code"):
                    with zipfile.ZipFile(
                        "generated_code.zip", "w", zipfile.ZIP_DEFLATED
                    ) as zipf:
                        for root, dirs, files in os.walk("generated_code"):
                            for file in files:
                                full_path = os.path.join(root, file)
                                zipf.write(
                                    full_path,
                                    os.path.relpath(full_path, "generated_code"),
                                )
                    print("Folder zipped successfully!!")

                    remove_dir("./generated_code")

                    st.markdown(
                        "### Download the zipped folder containing Feature File & Step Definitions:"
                    )
                    with open("./generated_code.zip", "rb") as file:
                        zip_data = file.read()

                    if st.download_button(
                        label="Download Zipped Testcases",
                        data=zip_data,
                        file_name="generated_code.zip",
                        mime="application/zip",
                    ):
                        st.session_state.downloaded = True
                else:
                    st.write(
                        "The generated test cases have been successfully downloaded!"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
    elif st.session_state.downloaded:
        st.stop()


def on_click_button():
    st.session_state.clear()

st.markdown(
    "<h1 style = 'text-align: center; color: green;'>QE-NextGen</h1>",
    unsafe_allow_html=True,
)

col_1, col_2 = st.columns([1, 3])
input_method = col_1.selectbox(
    "Select Input Method",
    [
        "URL",
        "User Story",
        "Feature File",
        "Epic/Jira Link",
        "Swagger Url",
        "Postman Collection",
    ],
    index=0,
    on_change=on_click_button,
)

if input_method == None:
    st.stop()

if input_method == "URL":
    input_url = col_2.text_input("Enter URL to identify Scenarios to automate").strip()

    if not input_url:
        st.stop()

    start = time.time()
    # By this stage, we get a list of all scenarios that can be automated
    resulting_features_list, html_text = st_scrape_and_extract_features(
        input_url, selected_option
    )
    end = time.time()
    print(f"Application took {end-start:0.2f} seconds to fetch all the scenarios")
    time_keeper.append(round(end-start, 2))

    # Sometimes, the xpath created by LLM are not correct.
    # Remove those xpaths from the list before presenting the data on UI.
    for xpath in resulting_features_list:
        if not extract_code_block(html_text, xpath["xpath"]):
            resulting_features_list.remove(xpath)

    # creating dataFrame from generated list
    df_feature_list = pd.DataFrame(resulting_features_list)

    # Dropping 'xpath' and renaming columns to show it to user on UI
    display_list = df_feature_list.drop(columns=["xpath"]).rename(
        columns={"name": "Scenarios generated for testing", "description": "Description of the Feature"}
    )
    st.dataframe(display_list, use_container_width=True)

    st.markdown("### Select Scenario")
    selected_feature = st.selectbox(
        "Select Scenario that you want to automate:",
        df_feature_list["name"],
        index=None,
        on_change=on_click_button,
    )

    if selected_feature == None:
        st.stop()

    selected_xpath = df_feature_list[df_feature_list["name"] == selected_feature][
        "xpath"
    ].values[0]

    start = time.time()
    code_block = extract_code_block(html_text, selected_xpath)
    end = time.time()
    time_keeper.append(round(end - start, 2))
    print("Code block for the selected scenario has been extracted successfully")

    start = time.time()
    final_code_block_summary = st_summarizer_function(code_block, selected_option)
    end = time.time()
    print(f"Application took {end-start:0.2f} seconds to generate summary")
    time_keeper.append(round(end - start, 2))

    st.markdown("### Code Block Summary")
    edited_summary = st.text_area("A consice summary about the scenario that you selected", final_code_block_summary)

    st.markdown("---")
    gherkin_syntax = ""

    # Generation and Download buttons
    col1, col2, _ = st.columns([2, 1, 1])
    generate_button = col1.button("Click here to generate the Feature file")

    # Removing the download button logic
    # if "messages" in st.session_state:
    #     with col2:
    #         create_download_button(gherkin_syntax, "_Feature.md")

    if generate_button:
        if "test_gen_count" in st.session_state:
            messages = st.session_state["messages"]
            # Run additional test case generation using the output from the previous step
            _, messages = st_create_additional_test_case(
                messages, selected_option
            )

        else:
            _, messages = st_create_initial_test_case(
                edited_summary, selected_option
            )

        st.session_state["test_gen_count"] = 1
        st.session_state["messages"] = messages

    if "messages" in st.session_state:
        gherkin_syntax = parse_assistant_output(st.session_state["messages"])
        # Display the final result
        st.code(gherkin_syntax, language="gherkin")

    # st.write(st.session_state['messages'])
    if "messages" not in st.session_state:
        st.stop()

    st.markdown("---")
    st.markdown("### Code Generation")

    scenario_list = fetch_scenarios_list(st.session_state["messages"])

    selected_scenario_name = st.selectbox(
        "Select scenario to generate code",
        [scenario["scenario_title"] for scenario in scenario_list],
        index=None,
    )

    if selected_scenario_name != None:
        scenario = next(
            (
                scenario
                for scenario in scenario_list
                if scenario["scenario_title"] == selected_scenario_name
            ),
            None,
        )

        scenario_str = generate_string_from_scenario([scenario])
        feature_header = fetch_feature_header(st.session_state["messages"])

        stepdefinition_file, locator_file, implementation_file = st_generate_code(
            feature_header + scenario_str,
            code_block,
            selected_option,
        )

        # stepdefinition_file, locator_file, implementation_file= "","",""
        try:
            # Create tabs
            tab1, tab2, tab3 = st.tabs(
                ["Step Definition File", "Implementation File", "Locator File"]
            )

            # Content for Tab 1
            with tab1:
                st.code(
                    re.search(r"`java\n(.*?)`", stepdefinition_file, re.DOTALL).group(1),
                    language="java",
                )

            # Content for Tab 2
            with tab2:
                st.code(re.search(r"`java\n(.*?)`", implementation_file, re.DOTALL).group(1), language="java")

            # Content for Tab 3
            with tab3:
                st.code(re.search(r"`java\n(.*?)`", locator_file, re.DOTALL).group(1), language="java")

        except:
            st.markdown("#### StepDefinition File")
            st.code(stepdefinition_file, language="java")
            st.markdown("#### Implementation File")
            st.code(implementation_file, language="java")
            st.markdown("#### Locator File")
            st.code(locator_file, language="java")

elif input_method == "Swagger Url":
    if "swagger_uri_generation" not in st.session_state:
        st.session_state.swagger_uri_generation = False
    
    # Initialize the session state variables if they are not already set
    if 'chunks' not in st.session_state:
        st.session_state.chunks = None

    if not st.session_state.swagger_uri_generation:
        url_to_scrape = col_2.text_input("Enter the Swagger URL to generate features.")
        if url_to_scrape == "":
            st.stop()
        
        if url_to_scrape:
            if url_to_scrape != st.session_state.get('last_url', ''):
                st.session_state.last_url = url_to_scrape
                st.session_state.swagger_uri_generation = False
                st.session_state.chunks = None  # Reset chunks to ensure fresh load
                
         
        if not st.session_state.swagger_uri_generation:       
            source_type = validate_type_of_request(url_to_scrape)
            # print("url_to_scrape:: ", url_to_scrape)
            if sys.platform == "win32":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            if source_type == "UI":
                if st.session_state.chunks is None:
                    st.session_state.chunks = asyncio.run(is_swagger_ui_url(url_to_scrape))
                    with open("exmaple.json", "w") as file:
                        json.dump(st.session_state.chunks, file)
                if st.session_state.chunks: 
                    tag_lists = process_chunks_to_list(st.session_state.chunks) 
                    # print(tag_lists)
                    if tag_lists:
                        selections = {}
                        for key, values in tag_lists.items():
                            options = st.multiselect(f"Select values for {key}:", values, key=key)
                            if options:
                                selections[key] = options
                            
                        if st.button('Process Selected Data'):
                            asyncio.run(process_selected_chunks(st.session_state.chunks,selections))
                            final_code_block_summary = "test fetched successfully"  
                            st.session_state.swagger_uri_generation = True
                            stop_api_rerun()
            else:
                print("Provided URL is invalid")
        

elif input_method == "Postman Collection":
    if "postman_generation" not in st.session_state:
        st.session_state.postman_generation = False
    if not st.session_state.postman_generation:
        postman_file = col_2.file_uploader(
            "Upload the Postman collection", type=["json"]
        )

        if postman_file is None:
            st.stop()

        # Parse the uploaded Postman collection file
        postman_collection = postman_file.read()
        postman_collection = json.loads(postman_collection)
        if postman_collection:
            chunks = traverse_collection(postman_collection)
            trigger_iam_user(chunks)
            final_code_block_summary = (
                "Your code has been Generated into the folder structure!!!"
            )
            st.session_state.postman_generation = True
            stop_api_rerun()
        else:
            print("postman collection data is invalid")

elif input_method == "User Story":
    user_input = col_2.text_area("Enter your user story here", key="user_story_input")

    if not user_input:
        st.stop()

    # Initialize session state components
    if 'ui' not in st.session_state:
        st.session_state.ui = {
            'tabs_initialized': False,
            'feature_file' : "",
            "step_definition_file" : "",
            "locator_file" : "",
            'implementation_file' :  ""
        }

    # Initial setup
    if 'response' not in st.session_state:
        st.session_state.response = generate_testcases_from_user_story_or_description(user_input, input_method)        
        # Initialize placeholders within each tab context
        response = st.session_state.response

        if response["status"] == 400:
            st.write(response["message"])
            st.stop()
        
        feature_file, locator_file, step_definition_file, implementation_file = response["message"]
        st.session_state.ui.update({
            'tabs_initialized': True,
            'feature_file' : feature_file,
            "step_definition_file" : step_definition_file,
            "locator_file" : locator_file,
            'implementation_file' :  implementation_file
        })
    
    if st.session_state.ui['tabs_initialized']:
        
        tab1,tab2,tab3, tab4 = st.tabs(["Feature File", "Step Definitions", "Implementation file", "Locators file"])
        with tab1:
            st.code(st.session_state.ui['feature_file'], language="gherkin")
        with tab2:
            st.code(st.session_state.ui['step_definition_file'], language="java")
        with tab3:
            st.code(st.session_state.ui['implementation_file'], language="java")
        with tab4:
            st.code(st.session_state.ui['locator_file'], language="java")
            

    with st.container():
        instructions = st.text_area("Enter modification instructions here", key="instructions_input")
        
        if st.button("Apply Modifications"):
            # Run modification function
            regenerate_as_per_instructions(instructions, user_input)
            
            # Regenerate content
            
            st.session_state.response = read_all_files()
            new_response = st.session_state.response
            
            if new_response["status"] != 400:
                st.session_state.response = new_response
                feature_file, locator_file, step_definition_file, implementation_file = new_response["message"]
                st.session_state.ui.update({
                    'tabs_initialized': True,
                    'feature_file' : feature_file,
                    "step_definition_file" : step_definition_file,
                    "locator_file" : locator_file,
                    'implementation_file' :  implementation_file
                })
                st.rerun()

elif input_method == "Epic/Jira Link":
    user_input = col_2.text_input("Enter your Epic/Jira link here")

    if not user_input:
        st.stop()

    response = (
        generate_testcases_from_user_story_or_description(user_input, input_method)
    )

    if response["status"] == 400:
        st.write(response["message"])
        st.stop()    

    feature_file, locator_file, step_definition_file, implementation_file = response["message"]

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Feature File", "Step Definition File", "Implementation File", "Locator File"]
    )

    # Content for Tab 1
    with tab1:
        st.code(feature_file, language="gherkin")

    # Content for Tab 2
    with tab2:
        st.code(step_definition_file, language="java")

    # Content for Tab 3
    with tab3:
        st.code(implementation_file, language="java")

    # Content for Tab 3
    with tab4:
        st.code(locator_file, language="java")

elif input_method == "Feature File":

    uploaded_file = st.file_uploader("Choose a file (.txt or .feature)", type=['txt', 'feature'])
    if uploaded_file is not None :
        # Convert filename to lowercase to ensure case insensitivity
        file_name = uploaded_file.name.lower()

        # Check if the file extension is correct
        if file_name.endswith('.txt') or file_name.endswith('.feature'):
            # Read file data
            data = uploaded_file.getvalue().decode('utf-8') 
            data = data.replace('\r\n', '\n')
            # Define the new filename and path to save
            new_file_path = os.path.join(os.getcwd(), 'feature_file.feature')

            # Save file data to a new file
            with open(new_file_path, 'w') as f:
                f.write(data)
            if not st.session_state.dir_names:
                st.session_state.dir_names = generate_test_cases_feature_file(new_file_path)

            st.write("Code Generated and Saved to Following Directories: ")
            for index, dir_path in enumerate(st.session_state.dir_names):
                abs_dir_path = os.path.abspath(dir_path)
                st.text(f"{index+1}. {abs_dir_path}")
    # else:
    #     st.error('Invalid file type uploaded. Please upload a .txt or .feature file.')

    if st.session_state.dir_names:
        # Let the user select a directory
        selected_dir = st.selectbox('Select a directory:', st.session_state.dir_names)

        if selected_dir:
            # Assume specific filenames are known and constant
            file_names = ['feature_file.feature', 'StepDefinition.java', 'Implementation.java', 'Locators.java']
            file_paths = [os.path.join(selected_dir, file_name) for file_name in file_names]

            # Check if files exist and then read them
            file_contents = []
            for path in file_paths:
                if os.path.exists(path):
                    with open(path, 'r') as file:
                        file_contents.append(file.read())
                else:
                    file_contents.append("File not found: " + path)

            # Tabs for displaying file contents
            tab1, tab2, tab3, tab4 = st.tabs(
                ["Feature File", "Step Definition File", "Implementation File", "Locator File"]
            )

            # Display each file content in its respective tab
            with tab1:
                st.code(file_contents[0], language="gherkin")

            with tab2:
                st.code(file_contents[1], language="java")

            with tab3:
                st.code(file_contents[2], language="java")

            with tab4:
                st.code(file_contents[3], language="java")
