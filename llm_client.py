from openai import OpenAI


class LLMClient:

    def __init__(self):

        self.client = OpenAI(
            api_key="s2_485ad5943af14dc4a6a663af88e4ef5e",
            base_url="https://routellm.abacus.ai/v1"
        )

    def ask(self, query, graph_data, vector_data):

        prompt = f"""
                You are an Enterprise Architecture,
                DevOps and Reliability expert.

                Use the supplied evidence to perform
                dependency and impact analysis.

                Do not use external knowledge.

                USER QUESTION:
                {query}

                GRAPH EVIDENCE:
                {graph_data}

                RETRIEVED EVIDENCE:
                {vector_data}

            Provide a concise response in this format:

            EXECUTIVE SUMMARY
            - 3 to 4 bullet points only

            CRITICAL DEPENDENCIES
            - List the most important dependencies

            BUSINESS IMPACT
            - Maximum 5 bullet points

            RISKS
            - Maximum 5 bullet points

            RECOMMENDATIONS
            - Maximum 5 bullet points

            Do not provide generic explanations.
            Do not provide assumptions.
            Use only the supplied graph and semantic evidence.
            Keep the response under 300 words.
            Use only information explicitly present in:

            1. Graph Dependencies
            2. Semantic Evidence

            If evidence is insufficient,
            respond with:

            "Not enough evidence available."

            Do not invent workflows,
                systems, dependencies or risks.

            Reference the evidence wherever possible.
            Only state impacts that can be directly inferred from the graph or semantic evidence.

            Use cautious language such as:
            - may impact
            - could affect
            - potential dependency

            Avoid definitive statements unless explicitly supported by evidence.
            """

        response = self.client.chat.completions.create(
            model="o4-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content