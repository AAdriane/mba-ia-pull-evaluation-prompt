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

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = yaml.safe_load(f)
        return next(iter(content.values()))

class TestPrompts:
    path = "prompts/bug_to_user_story_v2.yml"
    
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompt = load_prompts(self.path)
        assert "system_prompt" in prompt
        assert prompt["system_prompt"].strip() != ""

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompt = load_prompts(self.path)
        system = prompt.get("system_prompt", "").lower()

        assert ("você é" in system) or ("voce é" in system), "O 'system_prompt' deve definir uma persona com 'Você é ...'"

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt = load_prompts(self.path)
        system = prompt.get("system_prompt", "").lower()

        has_format = any(kw in system.lower() for kw in ("user story", "critério", "critérios de aceitação", "como um"))
        assert has_format, "O 'system_prompt' deve mencionar o formato esperado (ex.: 'Como um', 'Critérios de Aceitação' ou 'User Story')"

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt = load_prompts(self.path)
        system = prompt.get("system_prompt", "").lower()

        system_upper = system.upper()
        assert ("EXEMPLO" in system_upper) or ("###" in system) or ("---" in system), "O prompt deve conter exemplos (few-shot) claramente identificáveis"

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt = load_prompts(self.path)
        system = prompt.get("system_prompt", "")

        assert "TODO" not in system, "O 'system_prompt' não deve conter '[TODO]'"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompt = load_prompts(self.path)
        techniques = prompt.get("techniques_applied", [])

        assert len(techniques) >= 2, "O prompt deve listar as técnicas utilizadas (campo 'techniques_applied')."

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])