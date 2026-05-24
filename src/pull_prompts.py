"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """Faz pull do repositório leonanluppi/bug_to_user_story_v1 no LangSmith Hub
    e salva em prompts/bug_to_user_story_v1.yml. Retorna o Path do arquivo salvo ou None em caso de erro.
    """
    repo = "leonanluppi/bug_to_user_story_v1"
    path = Path("prompts/bug_to_user_story_v1.yml")
    print_section_header(f"Pulling prompts from: {repo}")

    try:
        prompt_obj = hub.pull(repo)
    except Exception as e:
        print(f"Error to load {repo}: {e}", file=sys.stderr)
        return None
    
    prompt = {
        'bug_to_user_story_v1': {
            'description': "Prompt para converter relatos de bugs em User Stories",
            'version': 'v1',
            'tags': ["bug-analysis", "user-story", "product-management"],
        }
    }

    if hasattr(prompt_obj, "messages"):
            try:
                for msg in prompt_obj.messages:
                    if (hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template')):
                        role = getattr(msg, 'role', None)
                        if ((role == "system")
                            or msg.__class__.__name__ == "SystemMessagePromptTemplate"
                        ):
                           prompt['bug_to_user_story_v1']['system_prompt'] = msg.prompt.template
                        elif ((role == "human")
                            or msg.__class__.__name__ == "HumanMessagePromptTemplate"
                        ):
                            prompt['bug_to_user_story_v1']['user_prompt'] = msg.prompt.template

            except Exception as e:
                print(f"Error processing prompt: {e}", file=sys.stderr)
                return None

    print(f"Save location: {path}")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        save_yaml(prompt, path)
    except Exception as e:
        print(f"Error saving file: {e}", file=sys.stderr)
        return None

    print(f"Prompt saved successfully!")

    return path

def main():
    """Função principal"""
    # Verifica se as variáveis de ambiente necessárias estão presentes.
    # Ajuste os nomes das variáveis se seu .env usar chaves diferentes para LangSmith.
    required_envs = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_envs):
        print(f"Missing environment variables", file=sys.stderr)
        return 2

    result = pull_prompts_from_langsmith()
    if result is None:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
