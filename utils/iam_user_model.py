import os
import json
import boto3
from dotenv import dotenv_values


def call_aws_bedrock_llm(
    prompt,
    model="meta.llama3-70b-instruct-v1:0",
    temperature=0,
    sys_prompt="You are a helpful AI assistant",
):
    # Create a Boto3 client for Bedrock
    bedrock_client = boto3.client(
        "bedrock-runtime",
        region_name=dotenv_values(".env")["AWS_REGION"],
        aws_access_key_id=dotenv_values(".env")["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=dotenv_values(".env")["AWS_SECRET_ACCESS_KEY"],
    )

    # Define Prompt Template
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
 
    {sys_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>
 
    {prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    # Define the payload
    payload = {
        "modelId": model,
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps(
            {
                "prompt": prompt,
                "temperature": temperature,
                "max_gen_len": 2048,
            }
        ),
    }

    # call Invoke model
    response = bedrock_client.invoke_model(
        modelId=payload["modelId"],
        contentType=payload["contentType"],
        accept=payload["accept"],
        body=payload["body"],
    )

    # Print the response
    llm_response = json.loads(response["body"].read())

    # return llm response
    return llm_response["generation"]
