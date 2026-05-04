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
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Ajustar path para importar utils
sys.path.insert(0, str(Path(__file__).parent))

from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt de bug_to_user_story do LangSmith Hub e salva localmente.
    """
    print_section_header("PULL DE PROMPTS DO LANGSMITH")

    prompt_name = "leonanluppi/bug_to_user_story_v1"
    output_path = PROJECT_ROOT / "prompts" / "bug_to_user_story_v1.yml"

    print(f"Fazendo pull do prompt: {prompt_name}")

    try:
        prompt = hub.pull(prompt_name)
        print(f"   ✓ Prompt carregado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt '{prompt_name}': {e}")
        return False

    # Extrair system e user prompts das mensagens
    system_prompt = ""
    user_prompt = ""

    for msg in prompt.messages:
        if isinstance(msg, SystemMessagePromptTemplate):
            system_prompt = msg.prompt.template
        elif isinstance(msg, HumanMessagePromptTemplate):
            user_prompt = msg.prompt.template

    if not system_prompt and not user_prompt:
        # Fallback: tentar via atributo messages genérico
        for msg in prompt.messages:
            role = getattr(msg, 'role', '') or type(msg).__name__.lower()
            template = ""
            if hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template'):
                template = msg.prompt.template
            elif hasattr(msg, 'content'):
                template = msg.content

            if 'system' in role.lower():
                system_prompt = template
            elif 'human' in role.lower() or 'user' in role.lower():
                user_prompt = template

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "source": prompt_name,
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    success = save_yaml(prompt_data, str(output_path))

    if success:
        print(f"   ✓ Prompt salvo em: {output_path}")
        return True
    else:
        print(f"❌ Erro ao salvar prompt em: {output_path}")
        return False


def main():
    """Função principal"""
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
