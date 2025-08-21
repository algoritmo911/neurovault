import spacy

class NLPProcessor:
    """
    A class to handle Natural Language Processing tasks using spaCy.
    """

    def __init__(self):
        """
        Initializes the NLP processor by loading the spaCy model.
        """
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading 'en_core_web_sm' model...")
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def extract_entities(self, text: str) -> list[tuple[str, str]]:
        """
        Extracts named entities from the given text.

        Args:
            text (str): The text to process.

        Returns:
            list[tuple[str, str]]: A list of tuples, where each tuple
                                   contains the entity text and its label.
        """
        doc = self.nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

    def extract_concepts(self, text: str) -> list[str]:
        """
        Extracts concepts (as noun chunks) from the given text.

        Args:
            text (str): The text to process.

        Returns:
            list[str]: A list of concepts.
        """
        doc = self.nlp(text)
        concepts = [chunk.text for chunk in doc.noun_chunks]
        return concepts

# Example usage (for testing purposes)
if __name__ == "__main__":
    processor = NLPProcessor()
    sample_text = (
        "Apple is looking at buying U.K. startup for $1 billion. "
        "The deal was discussed by Tim Cook and the CEO of the startup. "
        "They also talked about AI safety."
    )

    entities = processor.extract_entities(sample_text)
    print("Named Entities:", entities)

    concepts = processor.extract_concepts(sample_text)
    print("Concepts:", concepts)
