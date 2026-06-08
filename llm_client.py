from openai import OpenAI


class LLMClient:

    def __init__(self):

        self.client = OpenAI(
            api_key="s2_485ad5943af14dc4a6a663af88e4ef5e",
            base_url="https://routellm.abacus.ai/v1"
        )

    def ask(self, query, graph_data, vector_data):

        prompt = f"""
User Question:
{query}

Graph Analysis:
{graph_data}

Semantic Search Results:
{vector_data}

Provide:

1. Executive Summary
2. Impact Analysis
3. Risks
4. Recommendations
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content