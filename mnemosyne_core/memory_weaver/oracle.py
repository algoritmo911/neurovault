from .graph_db import GraphDB
from .nlp import NLPProcessor

class Oracle:
    """
    The Oracle module generates plausible hypotheses in response to complex,
    open-ended questions by finding relevant paths and patterns in the knowledge graph.
    """

    def __init__(self, db: GraphDB, nlp: NLPProcessor):
        """
        Initializes the Oracle with a database connection and an NLP processor.
        """
        self.db = db
        self.nlp = nlp

    def generate_hypotheses(self, question: str) -> list[str]:
        """
        Generates hypotheses based on a natural language question.

        This is a simplified implementation that extracts key entities and looks
        for simple connecting paths to nodes with noteworthy properties.
        """
        print(f"Oracle: Received question: '{question}'")

        # 1. Use NLP to find the main subjects of the question.
        # We'll look for Noun Chunks and Named Entities.
        concepts = self.nlp.extract_concepts(question)
        entities = [ent[0] for ent in self.nlp.extract_entities(question)]
        key_terms = list(set(concepts + entities))

        if not key_terms:
            return ["Could not identify any key terms in the question."]

        print(f"Oracle: Identified key terms: {key_terms}")

        hypotheses = []

        # 2. For each key term, run a pathfinding query.
        # We're looking for paths to nodes with "interesting" properties.
        # "Interesting" is defined here as having a negative status or sentiment.
        for term in key_terms:
            with self.db.driver.session() as session:
                query = """
                MATCH (start {name: $term})
                MATCH (end)
                WHERE end.status = 'deprecated' OR end.sentiment = 'negative' OR end.stress_level = 'high'
                MATCH p = allShortestPaths((start)-[*..3]-(end))
                RETURN p
                """
                results = session.run(query, term=term).data()

                # 3. Format the found paths into readable hypotheses.
                for record in results:
                    path = record['p']
                    hypotheses.append(self._format_path_as_hypothesis(path))

        return hypotheses if hypotheses else ["No clear hypotheses found based on the available data."]

    def _format_path_as_hypothesis(self, path) -> str:
        """
        Formats a Neo4j path object into a human-readable string.
        Example: (Node A)-[REL]->(Node B) => "Node A is related to Node B"
        """
        nodes = [node['name'] for node in path.nodes]
        rels = [rel.type for rel in path.relationships]

        hypothesis = f"Hypothesis: A path exists from '{nodes[0]}'"
        for i, rel in enumerate(rels):
            direction = "->" if path.relationships[i].start_node == path.nodes[i] else "<-"
            hypothesis += f" -[{rel}]- {direction} '{nodes[i+1]}'"

        final_node_properties = path.end_node.items()
        hypothesis += f", where {path.end_node['name']} has notable properties: {dict(final_node_properties)}."

        return hypothesis
