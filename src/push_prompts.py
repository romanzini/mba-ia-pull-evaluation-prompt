"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)

# Ajustar path para importar utils
sys.path.insert(0, str(Path(__file__).parent))

from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (ex: "meu_usuario/bug_to_user_story_v2")
        prompt_data: Dados do prompt extraídos do YAML

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_template = PromptTemplate.from_template(prompt_data["system_prompt"])
        user_template = PromptTemplate.from_template(prompt_data["user_prompt"])

        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate(prompt=system_template),
            HumanMessagePromptTemplate(prompt=user_template),
        ])

        print(f"   Fazendo push para: {prompt_name}")
        hub.push(prompt_name, chat_prompt, new_repo_is_public=True)
        print(f"   ✓ Push realizado com sucesso")
        print(f"   ✓ Disponível em: https://smith.langchain.com/hub/{prompt_name}")
        return True

    except Exception as e:
        print(f"   ❌ Erro ao fazer push do prompt '{prompt_name}': {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ["description", "system_prompt", "user_prompt", "version"]
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: '{field}'")

    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    user_prompt = prompt_data.get("user_prompt", "").strip()
    if not user_prompt:
        errors.append("user_prompt está vazio")

    if "[TODO]" in system_prompt or "[TODO]" in user_prompt:
        errors.append("Prompt ainda contém marcadores [TODO]")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(
            f"Mínimo de 2 técnicas requeridas em 'techniques_applied', encontradas: {len(techniques)}"
        )

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA O LANGSMITH")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurada no .env")
        return 1

    yaml_path = PROJECT_ROOT / "prompts" / "bug_to_user_story_v2.yml"
    print(f"Carregando prompt de: {yaml_path}\n")

    yaml_data = load_yaml(str(yaml_path))
    if not yaml_data:
        print(f"❌ Não foi possível carregar o arquivo: {yaml_path}")
        return 1

    # O YAML contém uma chave raiz com o nome do prompt
    prompt_key = "bug_to_user_story_v2"
    if prompt_key not in yaml_data:
        print(f"❌ Chave '{prompt_key}' não encontrada no YAML")
        print(f"   Chaves disponíveis: {list(yaml_data.keys())}")
        return 1

    prompt_data = yaml_data[prompt_key]

    # Validar antes de enviar
    print("Validando prompt...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("❌ Prompt inválido. Corrija os erros abaixo:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("   ✓ Prompt válido\n")

    # Exibir informações do prompt
    techniques = prompt_data.get("techniques_applied", [])
    print(f"Versão: {prompt_data.get('version', 'N/A')}")
    print(f"Descrição: {prompt_data.get('description', 'N/A')}")
    print(f"Técnicas aplicadas ({len(techniques)}):")
    for technique in techniques:
        print(f"   - {technique}")
    print()

    # Fazer push
    hub_prompt_name = f"{username}/{prompt_key}"
    success = push_prompt_to_langsmith(hub_prompt_name, prompt_data)

    if success:
        print(f"\n✅ Prompt publicado com sucesso!")
        print(f"\nPróximos passos:")
        print(f"1. Verifique o prompt em: https://smith.langchain.com/hub/{hub_prompt_name}")
        print(f"2. Certifique-se de que está marcado como público")
        print(f"3. Execute a avaliação: python src/evaluate.py")
        return 0
    else:
        print(f"\n❌ Falha ao publicar o prompt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
