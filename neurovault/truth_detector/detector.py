import json

class TruthDetector:
    """
    A class to analyze data items and classify them as fact, fiction,
    or unverifiable using a simulated LLM call.
    """

    def _build_prompt(self, text_content: str) -> str:
        """Constructs the prompt for the LLM."""
        prompt = (
            "Проанализируй следующий текст. Оцени, является ли он фактом, "
            "вымыслом или информацией, не поддающейся проверке. "
            "Оцени свою уверенность по шкале от 0.0 до 1.0. "
            "Дай краткое обоснование.\n\n"
            f"Текст для анализа: \"{text_content}\"\n\n"
            "Требуемый формат ответа - строго заданный JSON: "
            '{ "classification": "fact" | "fiction" | "unverifiable", '
            '"confidence_score": 0.0-1.0, "reasoning": "..." }'
        )
        return prompt

    def _call_llm(self, prompt: str) -> str:
        """
        Simulates a call to an LLM. In a real implementation, this method
        would contain the code to interact with an LLM API.
        """
        # Mocked response for demonstration purposes.
        mock_response = {
            "classification": "fact",
            "confidence_score": 0.85,
            "reasoning": "The statement contains verifiable historical details."
        }
        return json.dumps(mock_response, ensure_ascii=False)

    def analyze(self, data_item: dict) -> dict:
        """
        Analyzes a single data item.

        Args:
            data_item: A dictionary representing the data item, expected
                       to have a 'content' key with the text to analyze.

        Returns:
            A dictionary with the analysis result.
        """
        # For now, we assume the text is in a 'content' field.
        # This can be adjusted based on the actual data structure from the pipeline.
        text_content = data_item.get("content", "")
        if not text_content:
            # Handle cases where content is missing or empty
            return {
                "classification": "unverifiable",
                "confidence_score": 1.0,
                "reasoning": "The data item had no text content to analyze."
            }

        prompt = self._build_prompt(text_content)

        # In a real scenario, we would send the prompt to the LLM
        # and parse the response.
        print(f"--- Generated Prompt ---\n{prompt}\n----------------------")

        llm_response_str = self._call_llm(prompt)

        try:
            analysis_result = json.loads(llm_response_str)
        except json.JSONDecodeError:
            # Handle cases where the LLM response is not valid JSON
            # This is a fallback for a real-world scenario.
            return {
                "classification": "unverifiable",
                "confidence_score": 0.0,
                "reasoning": "Failed to parse the analysis result from the LLM."
            }

        return analysis_result
