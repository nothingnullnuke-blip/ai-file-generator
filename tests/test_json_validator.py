from ai_engine.json_validator import JSONValidator
import json

def test_json_extraction():
    raw = '{"title": "Test", "sections": []}'
    result = JSONValidator.validate_and_repair(raw)
    assert result is not None
    assert result['title'] == "Test"

def test_json_repair():
    raw = '{"title": "Test", "sections": [],}'
    result = JSONValidator.validate_and_repair(raw)
    assert result is not None
    assert 'title' in result

def test_json_with_markdown():
    raw = '```json\n{"title": "Test", "sections": []}\n```'
    result = JSONValidator.validate_and_repair(raw)
    assert result is not None
    assert result['title'] == "Test"

def test_default_template():
    raw = "not valid json at all"
    result = JSONValidator.validate_and_repair(raw)
    assert result is not None
    assert 'title' in result
    assert 'sections' in result