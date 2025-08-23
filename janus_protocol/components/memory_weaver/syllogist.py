import yaml
from .graph_db import GraphDB
import re

class Syllogist:
    """
    The Syllogist module is the inference engine for the MemoryWeaver.
    It uses a set of rules to deduce new facts and relationships from the
    existing data in the knowledge graph.
    """

    def __init__(self, rules_path='mnemosyne_core/memory_weaver/rules.yaml'):
        """
        Initializes the Syllogist by loading the inference rules.
        """
        with open(rules_path, 'r') as f:
            self.rules = yaml.safe_load(f)
        self.db = GraphDB()

    def run_inference(self):
        """
        Runs the inference process by executing all loaded rules.
        """
        print("Syllogist: Starting inference run...")
        for rule in self.rules:
            print(f"Syllogist: Executing rule '{rule['name']}'...")
            self._execute_rule(rule)
        print("Syllogist: Inference run complete.")

    def _execute_rule(self, rule: dict):
        """
        Executes a single inference rule.

        This involves:
        1. Constructing a MATCH query from the 'if' conditions.
        2. Executing the query to find all matching patterns.
        3. For each match, creating the new inferred relationship from the 'then' clause.
        """
        # --- 1. Construct the MATCH query ---
        match_clauses = "MATCH " + ", ".join(rule['if'])

        # Extract all unique variable names (e.g., 'person', 'project') from the rule
        variables = re.findall(r'\((\w+):', " ".join(rule['if']))
        unique_variables = sorted(list(set(variables)))

        return_clause = "RETURN " + ", ".join([f"elementId({v}) AS {v}_id" for v in unique_variables])

        where_clauses = ""
        if 'where' in rule:
            where_clauses = " WHERE " + " AND ".join(rule['where'])

        match_query = f"{match_clauses}{where_clauses} {return_clause}"

        # --- 2. Execute the MATCH query ---
        with self.db.driver.session() as session:
            results = session.run(match_query).data()

            # --- 3. For each match, create the inferred relationship ---
            for record in results:
                then_clause = rule['then'][0] # Assuming one 'then' for simplicity for now
                create_pattern = then_clause['create']
                properties = then_clause.get('properties', {})

                # Build the creation query
                # We use elementId to ensure we match the exact nodes from the previous query
                create_match_parts = []
                for var in unique_variables:
                    create_match_parts.append(f"MATCH ({var}) WHERE elementId({var}) = ${var}_id")

                create_match_clause = " ".join(create_match_parts)

                # Replace variable placeholders in the create pattern with the actual variables
                # This is a simplification; a more robust solution would parse the pattern
                final_create_pattern = create_pattern

                create_query = (
                    f"{create_match_clause} "
                    f"MERGE {final_create_pattern} "
                    "SET r += $properties"
                )

                # Prepare parameters for the creation query
                params = {f"{var}_id": record[f"{var}_id"] for var in unique_variables}
                params['properties'] = properties

                # Use a write transaction to create the new relationship
                session.write_transaction(lambda tx: tx.run(create_query, **params))

            print(f"Syllogist: Rule '{rule['name']}' affected {len(results)} records.")

# Example usage
if __name__ == "__main__":
    syllogist = Syllogist()
    syllogist.run_inference()
