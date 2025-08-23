import pytest
from janus_protocol.psychographer import Psychographer

def test_psychographer_analysis(tmp_path):
    """
    Tests the Psychographer's ability to analyze a source file and
    build a correct user model.
    """
    # 1. Create a dummy source file with known characteristics
    source_content = """
# Project Janus

This is a test of the Psychographer.

* It should find entities like Katana.
* It should count list items.

The user also mentions "game theory".

```python
# This is a code block
print("Hello, World!")
```
"""
    source_file = tmp_path / "test_source.md"
    source_file.write_text(source_content, encoding="utf-8")

    # 2. Run the Psychographer on the new file
    psychographer = Psychographer()
    psychographer.analyze_source_text(str(source_file))

    # 3. Get the model and assert its contents
    model = psychographer.get_model()

    # Assertions for the cognitive profile (style analysis)
    style = model["cognitive_profile"]["style"]
    assert style["headings"] == 1, "Should have found 1 heading"
    assert style["list_items"] == 2, "Should have found 2 list items"
    assert style["code_blocks"] == 1, "Should have found 1 code block"

    # Assertions for the knowledge graph (entity/concept extraction)
    kg = model["knowledge_graph"]
    assert kg["entities"]["Katana"] == 1, "Should have found the 'Katana' entity"
    assert "game theory" in kg["concepts"], "Should have found the 'game theory' concept"
    assert kg["concepts"]["game theory"] == 1
