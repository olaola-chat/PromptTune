import anthropic
import json
client = anthropic.Anthropic()

response = client.messages.count_tokens(
    model="claude-3-7-sonnet-20250219",
    system="You are a scientist",
    messages=[{
        "role": "user",
        "content": "Hello, Claude"
    }],
)

print( json.loads(response.model_dump_json())["input_tokens"])  
