import anthropic,re
from core.prompt.prompt_template import METAPROMPT,remove_floating_variables_prompt
import dotenv
import os
dotenv.load_dotenv()


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") # Put your API key here!
MODEL_NAME = "claude-3-7-sonnet-20250219"
CLIENT = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def pretty_print(message):
    print('\n\n'.join('\n'.join(line.strip() for line in re.findall(r'.{1,100}(?:\s+|$)', paragraph.strip('\n'))) for paragraph in re.split(r'\n\n+', message)))

def extract_between_tags(tag: str, string: str, strip: bool = False) -> list[str]:
    ext_list = re.findall(f"<{tag}>(.+?)</{tag}>", string, re.DOTALL)
    if strip:
        ext_list = [e.strip() for e in ext_list]
    return ext_list

def remove_empty_tags(text):
    return re.sub(r'\n<(\w+)>\s*</\1>\n', '', text, flags=re.DOTALL)

def strip_last_sentence(text):
    sentences = text.split('. ')
    if sentences[-1].startswith("Let me know"):
        sentences = sentences[:-1]
        result = '. '.join(sentences)
        if result and not result.endswith('.'):
            result += '.'
        return result
    else:
        return text

def extract_prompt(metaprompt_response):
    between_tags = extract_between_tags("Instructions", metaprompt_response)[0]
    return between_tags[:1000] + strip_last_sentence(remove_empty_tags(remove_empty_tags(between_tags[1000:]).strip()).strip())

def extract_variables(prompt):
    pattern = r'{([^}]+)}'
    variables = re.findall(pattern, prompt)
    return set(variables)

def remove_inapt_floating_variables(prompt):
    message = CLIENT.messages.create(
        model=MODEL_NAME,
        messages=[{'role': "user", "content": remove_floating_variables_prompt.replace("{$PROMPT}", prompt)}],
        max_tokens=4096,
        temperature=0
    ).content[0].text
    return extract_between_tags("rewritten_prompt", message)[0]

def find_free_floating_variables(prompt):
    variable_usages = re.findall(r'\{\$[A-Z0-9_]+\}', prompt)

    free_floating_variables = []
    for variable in variable_usages:
        preceding_text = prompt[:prompt.index(variable)]
        open_tags = set()

        i = 0
        while i < len(preceding_text):
            if preceding_text[i] == '<':
                if i + 1 < len(preceding_text) and preceding_text[i + 1] == '/':
                    closing_tag = preceding_text[i + 2:].split('>', 1)[0]
                    open_tags.discard(closing_tag)
                    i += len(closing_tag) + 3
                else:
                    opening_tag = preceding_text[i + 1:].split('>', 1)[0]
                    open_tags.add(opening_tag)
                    i += len(opening_tag) + 2
            else:
                i += 1

        if not open_tags:
            free_floating_variables.append(variable)

    return free_floating_variables


def get_response(task_description: str=""):
    TASK = """
            AI恋爱专家需求：
            服务集成在公司内项目，评估聊天关系，辅助聊天
            评估ai与人的聊天关系
            集成在主播助手上，评估聊天关系，辅助聊天
            """

    prompt = METAPROMPT.replace("{{TASK}}", TASK)

    response = CLIENT.messages.create(
                                    model=MODEL_NAME,
                                    max_tokens=4096,
                                    messages=[
                                        {
                                            "role": "user",
                                            "content":  prompt
                                        }
                                    ]
                                    )
    
    print(response.model_dump_json())

    return response.content[0].text



if __name__ == "__main__":
    message = get_response()
    # extracted_prompt_template = extract_prompt(message)
    # variables = extract_variables(message)

    # print("Variables:\n\n" + str(variables))
    # print("\n************************\n")
    # print("Prompt:")
    # pretty_print(extracted_prompt_template)
    # print("\n************End Prompt************\n")
    # floating_variables = find_free_floating_variables(extracted_prompt_template)
    # if len(floating_variables) > 0:
    #     extracted_prompt_template_old = extracted_prompt_template
    #     extracted_prompt_template = remove_inapt_floating_variables(extracted_prompt_template)
    #     print("New prompt template:\n")
    #     pretty_print(extracted_prompt_template)