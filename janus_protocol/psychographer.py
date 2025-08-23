import re
from collections import Counter
from janus_protocol.components.memory_weaver.nlp import NLPProcessor

class Psychographer:
    """
    The Psychographer daemon is responsible for building and maintaining a
    dynamic, high-fidelity model of the user's cognitive state.
    """

    def __init__(self):
        """Initializes the Psychographer and its components."""
        self.nlp_processor = NLPProcessor()
        self.knowledge_graph = {
            "entities": Counter(),
            "concepts": Counter()
        }
        self.cognitive_profile = {
            "style": {
                "headings": 0,
                "list_items": 0,
                "code_blocks": 0
            },
            "line_count": 0
        }
        print("Psychographer initialized.")

    def analyze_source_text(self, filepath: str):
        """
        Analyzes a given text file to update the user model.

        Args:
            filepath: The path to the text file to analyze.
        """
        print(f"Psychographer: Analyzing source '{filepath}'...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

            self._build_knowledge_graph(text)
            self._build_cognitive_profile(text)
        except FileNotFoundError:
            print(f"Psychographer: ERROR - File not found at '{filepath}'.")
        except Exception as e:
            print(f"Psychographer: ERROR - Failed to analyze '{filepath}': {e}")

    def _build_knowledge_graph(self, text: str):
        """Extracts entities and concepts to build the knowledge graph."""
        entities = self.nlp_processor.extract_entities(text)
        concepts = self.nlp_processor.extract_concepts(text)

        self.knowledge_graph["entities"].update([ent[0] for ent in entities])
        self.knowledge_graph["concepts"].update(concepts)

    def _build_cognitive_profile(self, text: str):
        """Analyzes the text to build a cognitive/stylistic profile."""
        lines = text.splitlines()
        self.cognitive_profile["line_count"] += len(lines)

        # Count code blocks first, as they can contain characters that mimic other styles
        num_code_blocks = len(re.findall(r"```", text)) // 2
        self.cognitive_profile["style"]["code_blocks"] += num_code_blocks

        # Create a version of the text with code blocks removed to avoid false positives
        text_without_code = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

        # Count headings (lines starting with #) on the sanitized text
        self.cognitive_profile["style"]["headings"] += len(re.findall(r"^\s*#+\s", text_without_code, re.MULTILINE))

        # Count list items (lines starting with * or -) on the sanitized text
        self.cognitive_profile["style"]["list_items"] += len(re.findall(r"^\s*[\*\-]\s", text_without_code, re.MULTILINE))

    def get_model(self) -> dict:
        """
        Returns the final, aggregated psychographic model.
        Converts Counters to regular dicts for JSON serialization.
        """
        return {
            "knowledge_graph": {
                "entities": dict(self.knowledge_graph["entities"]),
                "concepts": dict(self.knowledge_graph["concepts"])
            },
            "cognitive_profile": self.cognitive_profile
        }
