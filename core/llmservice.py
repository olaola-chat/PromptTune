import os, json, logging
from typing import Dict, List, Optional, Callable
from .model_config import get_model_config, ModelConfig
from .prompt.prompt_template import METAPROMPT
from .tools import extract_prompt
import boto3
import anthropic
import dotenv

dotenv.load_dotenv()

class LLMService:
    def __init__(self, model_name: Optional[str] = None, logger=None):
        """Initialize the LLM service with API key and optional model name."""
        self.client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.bedrock_client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_BEDROCK_REGION"))
        self.bedrock_model_id = os.getenv("AWS_BEDROCK_MODEL_ID")
        self._config = get_model_config(model_name)
        self.logger = logger or logging.getLogger(__name__)
        
    @property
    def model_config(self) -> ModelConfig:
        """Get current model configuration."""
        return self._config

    def set_model(self, model_name: str) -> None:
        """Set the model configuration by name."""
        self._config = get_model_config(model_name)

    def generate_prompt(self, task: str, thinking_mode: bool = False, progress_callback: Optional[Callable[[int, str], None]] = None) -> str:
        """Generate a prompt based on task description and optional parameters."""
        try:
            if progress_callback:
                progress_callback(0, "Starting prompt generation...")

            # Generate prompt using template
            prompt = METAPROMPT.replace("{{TASK}}", task)
            self.logger.info(prompt)
 
            if progress_callback:
                progress_callback(0, "Preparing API request...")

            if thinking_mode:
                self.logger.info("Thinking mode enabled")
                response = self.client.messages.create(
                    model=self._config.name,
                    max_tokens=self._config.max_tokens,
                    temperature=self._config.temperature,
                    messages=[
                        {
                            "role": "user",
                            "content":  prompt
                        }
                    ],
                    thinking={
                        "type": "enabled",
                        "budget_tokens": self._config.thinking["budget_tokens"]
                    },
                )
            else:
                response = self.client.messages.create(
                    model=self._config.name,
                    max_tokens=self._config.max_tokens,
                    temperature=self._config.temperature,
                    messages=[
                        {
                            "role": "user",
                            "content":  prompt
                        }
                    ],
                )

            if progress_callback:
                progress_callback(0, "Processing response...")

            response_json = json.loads(response.model_dump_json())
    
            self.logger.info(f"Input Tokens: {response_json['usage']['input_tokens']}")
            self.logger.info(f"Output Tokens: {response_json['usage']['output_tokens']}")

            result = response.content[0].text
            self.logger.info(f"Result:  {result}")
            extracted_prompt_template = extract_prompt(result)

            
            if progress_callback:
                progress_callback(0, "Finalizing prompt...")

            return extracted_prompt_template
        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            raise Exception(f"Error generating prompt: {str(e)}")

    def generate_prompt_bedrock(self, task: str, thinking_mode: bool = False, progress_callback: Optional[Callable[[int, str], None]] = None) -> str:
        try:
            if progress_callback:
                progress_callback(0, "Starting prompt generation...")

            # Generate prompt using template
            prompt = METAPROMPT.replace("{{TASK}}", task)
          
 
            if progress_callback:
                progress_callback(0, "Preparing API request...")

            if thinking_mode:
                self.logger.info("Thinking mode enabled")

                native_request = {
                                "anthropic_version": "bedrock-2023-05-31",
                                "max_tokens": self._config.max_tokens,
                                "temperature": 1,
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": [{"type": "text", "text": prompt}],
                                    }
                                ],
                                "thinking": {
                                    "type": "enabled",
                                    "budget_tokens": self._config.thinking["budget_tokens"]
                                }
                            }
                request = json.dumps(native_request)
                response = self.bedrock_client.invoke_model(modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0", body=request)
                response_body = json.loads(response['body'].read()) 

            else:
                native_request = {
                                "anthropic_version": "bedrock-2023-05-31",
                                "max_tokens": self._config.max_tokens,
                                "temperature": self._config.temperature,
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": [{"type": "text", "text": prompt}],
                                    }
                                ]
                            }
                request = json.dumps(native_request)
                response = self.bedrock_client.invoke_model(modelId=self.bedrock_model_id, body=request)
                response_body = json.loads(response['body'].read())     


            if progress_callback:
                progress_callback(0, "Processing response...")
    
            self.logger.info(f"Input Tokens: {response_body['usage']['input_tokens']}")
            self.logger.info(f"Output Tokens: {response_body['usage']['output_tokens']}")

            if thinking_mode:
                result = response_body['content'][1]['text']
            else:
                result = response_body['content'][0]['text']

            self.logger.info(f"Result:  {result}")
            extracted_prompt_template = extract_prompt(result)

            
            if progress_callback:
                progress_callback(0, "Finalizing prompt...")

            return extracted_prompt_template
        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            raise Exception(f"Error generating prompt: {str(e)}")

    # def test_prompt(self, prompt_template: str, test_input: Dict[str, str]) -> str:
    #     """Test a prompt template with provided variable values."""
    #     try:
    #         # Replace variables in the prompt template
    #         for key, value in test_input.items():
    #             prompt_template = prompt_template.replace(f"{{{key}}}", str(value))

    #         # Call Anthropic API
    #         response = self.client.completion(
    #             prompt=prompt_template,
    #             model=self._config.name,
    #             max_tokens_to_sample=self._config.max_tokens,
    #             temperature=self._config.temperature,
    #         )

    #         return response['completion']
    #     except Exception as e:
    #         raise Exception(f"Error testing prompt: {str(e)}")

    def update_config(self, **kwargs) -> None:
        """Update the current model configuration parameters."""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                raise ValueError(f"Invalid configuration parameter: {key}")
