"""
This module contains the EmbeddingGenerator class for converting text to vector embeddings.
"""
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    """
    A class to generate embeddings for text using a pre-trained model.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the EmbeddingGenerator with a specified model.

        Args:
            model_name (str): The name of the sentence-transformer model to use.
        """
        self.model = SentenceTransformer(model_name)

    def vectorize(self, text: str) -> list[float]:
        """
        Generates a vector embedding for the given text.

        Args:
            text (str): The input text to vectorize.

        Returns:
            list[float]: The vector embedding of the text.
        """
        embedding = self.model.encode(text)
        return embedding.tolist()


if __name__ == '__main__':
    generator = EmbeddingGenerator()
    test_sentence = "This is a test sentence for the embedding generator."
    vector = generator.vectorize(test_sentence)
    print(f"Shape of the vector: {len(vector)}")
    print(f"First 5 elements of the vector: {vector[:5]}")
