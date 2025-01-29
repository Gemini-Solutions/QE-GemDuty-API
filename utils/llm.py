import boto3
import json
from dotenv import dotenv_values
from openai import OpenAI
import os
# TODO : why is this still getting used - need to make a separate function for the calling all the llms at using the same function ? 
def call_llm(
    conversation,
    temperature=1.0,
    max_tokens=None,
    user=None,
    stream=False,
    seed=34,
    response_format="text",
    model="gpt-4o",
):

    client = OpenAI(
        api_key=dotenv_values(".env")["GPT_SECRET_KEY"],
    )

    # Define conversation with JSON system message
    if isinstance(conversation, str) and response_format == 'text':
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": conversation}
        ]
    elif isinstance(conversation, str) and response_format == 'json_object':
        messages = [
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": conversation}
        ]
    elif isinstance(conversation, list):
        messages = conversation
    else:
        print("Incorrect Conversation/Message format.")

    # Create chat completion
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        user=user,
        stream=stream,
        seed=seed,
        response_format={"type" : response_format}
    )

    # Print or return the generated poem
    response_generated = completion.choices[0].message
    finish_reason = completion.choices[0].finish_reason
    token_usage = completion.usage

    llm_output = {
        "response_generated": response_generated,
        "finish_reason": finish_reason,
        "token_usage": dict(token_usage)
    }

    return llm_output

# TODO : scrap  this and use llm_call.py file every where 
def call_aws_bedrock_llm(
    prompt,
    model="meta.llama3-70b-instruct-v1:0",
    temperature=0,
    sys_prompt="You are a helpful AI assistant",
):
    # Create a Boto3 client for Bedrock
    bedrock_client = boto3.client(
        "bedrock-runtime",
        region_name="ap-south-1",
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
                "prompt" : prompt,
                "temperature" : temperature,
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

    # Print or return the generated poem
    response_generated = llm_response["generation"]
    finish_reason = llm_response["stop_reason"]
    prompt_token_count = llm_response["generation_token_count"]
    generation_token_count = llm_response["generation_token_count"]
    total_tokens = prompt_token_count + generation_token_count

    llm_output = {
        "response_generated": response_generated,
        "finish_reason": finish_reason,
        "token_usage": {
            "completion_tokens": generation_token_count,
            "prompt_tokens": prompt_token_count,
            "total_tokens": total_tokens,
        },
    }

    return llm_output

# TODO : scrap this and use llm_call.py file every where

def call_anthropic_model(
    prompt,
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    temperature=0,
    sys_prompt="You are a helpful AI assistant",
):

    # Create a Boto3 client for Bedrock
    bedrock_client = boto3.client(
        "bedrock-runtime",
        region_name="us-west-2",
        aws_access_key_id=dotenv_values(".env")["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=dotenv_values(".env")["AWS_SECRET_ACCESS_KEY"]
    )

    # Format the request payload using the model's native structure.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 8192,
        "temperature": 0.1,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    # # Convert the native request to JSON.
    request = json.dumps(native_request)

    # # Invoke the model with the request.
    streaming_response = bedrock_client.invoke_model_with_response_stream(
        modelId=model, body=request
    )

    output = ""
    # Extract and print the response text in real-time.
    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk["type"] == "content_block_delta":
            output += chunk["delta"].get("text", "")
            # print(chunk["delta"].get("text", ""), end="")

    llm_output = {
        "response_generated": output,
        "finish_reason": "stop",
        "token_usage": {
            "completion_tokens": "2048",
            "prompt_tokens": "2048",
            "total_tokens": "4096",
        },
    }

    return llm_output
