# Use the native inference API to send a text message to Anthropic Claude.

import boto3
import json
import os
import dotenv
from botocore.exceptions import ClientError

dotenv.load_dotenv()

# Create a Bedrock Runtime client in the AWS Region of your choice.
client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_BEDROCK_REGION"))

# Set the model ID, e.g., Claude 3 Haiku.
model_id = os.getenv("AWS_BEDROCK_MODEL_ID")

# Define the prompt for the model.
prompt = "what is CoT?"

# Format the request payload using the model's native structure.
native_request = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 2000,
    "temperature": 1,
    "messages": [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }
    ],
    "thinking": {
        "type": "enabled",
        "budget_tokens": 1024
    }
}

# Convert the native request to JSON.
request = json.dumps(native_request)

try:
    # Invoke the model with the request.
    response = client.invoke_model(modelId=model_id, body=request)
    response_body = json.loads(response['body'].read())

    #print(response_body)

except (ClientError, Exception) as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)

# # Decode the response body.
# model_response = json.loads(response["body"].read())

# # Extract and print the response text.
response_thinking_text = response_body["content"][0]['thinking']
response_text = response_body["content"][1]['text']
print(response_thinking_text)
print("--------------------------------")
print(response_text)
