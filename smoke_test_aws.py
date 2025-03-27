import boto3
import json

bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

request = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 2000,
    "messages": [
        {
            "role": "user",
            "content": "Outline a migration strategy from on-prem to AWS cloud"
        }
    ],
    "thinking": {
        "type": "enabled",
        "budget_tokens": 1024
    }
}

response = bedrock_runtime.invoke_model(
    modelId='us.anthropic.claude-3-7-sonnet-20250219-v1:0', 
    body=json.dumps(request)
)

response_body = json.loads(response['body'].read())

# Find the 'text' content block in the response
text_content = None
for content_block in response_body['content']:
    if content_block['type'] == 'text':
        text_content = content_block['text']
        break

print(text_content)