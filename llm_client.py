from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI


class LLMClient:

    def __init__(self):

        
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
          )

    def ask(self, query, graph_data, vector_data):

        prompt = f"""
                You are an Enterprise Architecture,
                DevOps and Reliability expert.

                Every statement must be directly supported by either:
                - Graph Evidence
                - Semantic Evidence

                If a statement is not supported by the supplied evidence, do not include it.

                Do not infer additional business impacts beyond the retrieved evidence.

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
            Describe what business activities could be affected.

            Avoid repeating role names.

            Instead explain the business consequence.

            RISKS
            - Maximum 5 bullet points

            RECOMMENDATIONS
            - Maximum 5 bullet points
            Recommend only actions that directly address the identified dependencies or bottlenecks.

            Do not recommend technologies or solutions that are not implied by the supplied evidence.         
            Be specific.

            Prefer evidence over general knowledge.

            Every bullet should be traceable to the supplied Graph or Semantic evidence.
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
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content