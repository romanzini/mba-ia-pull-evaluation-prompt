"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_prompt_data():
    """Retorna os dados do prompt v2."""
    data = load_prompts(str(PROMPT_FILE))
    return data[PROMPT_KEY]


class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompt_data = get_prompt_data()
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado no YAML"
        assert prompt_data["system_prompt"], "Campo 'system_prompt' está vazio"
        assert prompt_data["system_prompt"].strip(), "Campo 'system_prompt' contém apenas espaços"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompt_data = get_prompt_data()
        system_prompt = prompt_data.get("system_prompt", "")
        role_keywords = ["você é", "voce é", "você é um", "you are", "você atua como"]
        has_role = any(kw.lower() in system_prompt.lower() for kw in role_keywords)
        assert has_role, (
            "O system_prompt não define uma persona/papel. "
            "Inclua algo como 'Você é um Product Manager...'"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt_data = get_prompt_data()
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")
        full_text = system_prompt + " " + user_prompt

        format_keywords = ["markdown", "user story", "como um", "critérios de aceitação", "dado que"]
        has_format = any(kw.lower() in full_text.lower() for kw in format_keywords)
        assert has_format, (
            "O prompt não menciona o formato esperado (Markdown, User Story, Critérios de Aceitação, etc.)"
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt_data = get_prompt_data()
        system_prompt = prompt_data.get("system_prompt", "")

        # Verifica indícios de exemplos no system prompt
        example_keywords = ["exemplo", "example", "relato de bug:", "user story gerada:", "bug report:"]
        has_examples = any(kw.lower() in system_prompt.lower() for kw in example_keywords)
        assert has_examples, (
            "O system_prompt não contém exemplos de entrada/saída (Few-shot Learning). "
            "Adicione pelo menos um par de exemplo bug_report → user story."
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_data = get_prompt_data()
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")
        full_text = system_prompt + " " + user_prompt

        assert "[TODO]" not in full_text, (
            "O prompt ainda contém marcadores [TODO]. Remova-os antes de usar."
        )
        assert "[todo]" not in full_text.lower(), (
            "O prompt ainda contém marcadores [TODO] (case-insensitive). Remova-os."
        )

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompt_data = get_prompt_data()
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list), (
            "O campo 'techniques_applied' deve ser uma lista no YAML"
        )
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas em 'techniques_applied', "
            f"encontradas: {len(techniques)}. Adicione técnicas como Few-shot, CoT, Role Prompting, etc."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])