
import os
import boto3
import json
from json_repair import repair_json
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()
# TODO : remove this - not getting used any where - merge this with call_anthropic_model -
def call_aws_bedrock_llm(
    prompt,
    model="meta.llama3-70b-instruct-v1:0",
    temperature=0,
    sys_prompt="You are a helpful AI assistant",
):
    # Create a Boto3 client for Bedrock
    bedrock_client = boto3.client(
        "bedrock-runtime",
        region_name="us-west-2",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
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
    llm_response = json.loads(repair_json(response["body"].read()))

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

    return llm_output["response_generated"]

def call_anthropic_model(
    prompt : str,
    # model="meta.llama3-70b-instruct-v1:0",
    model: str ="anthropic.claude-3-5-sonnet-20240620-v1:0",
    temperature=0,
    sys_prompt="You are a helpful AI assistant",
) -> str:
    
    client = boto3.client("bedrock-runtime", region_name="us-west-2",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
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
    streaming_response = client.invoke_model_with_response_stream(
        modelId=model, body=request
    )


    output=""
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

    return llm_output["response_generated"]



