import json
from openai import OpenAI
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


class QueryProcessor:
    def __init__(self, openai_api_key, perplexity_api_key):
        # Initialize OpenAI client for query generation
        self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Initialize Perplexity client for query processing
        self.perplexity_client = OpenAI(
            api_key=perplexity_api_key,
            base_url="https://api.perplexity.ai"
        )

    def generate_queries(self, research_query):
        """Generate queries using OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": "Generate a series of relevant queries based on a user's research topic or question."
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": research_query}]
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "query_set",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "queries": {
                                    "type": "array",
                                    "description": "A list of queries without any associated parameters or additional information.",
                                    "items": {
                                        "type": "string",
                                        "description": "A query string."
                                    }
                                }
                            },
                            "required": ["queries"],
                            "additionalProperties": False
                        }
                    }
                },
                temperature=1,
                max_tokens=10000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            queries = json.loads(response.choices[0].message.content)
            return queries['queries']
            
        except Exception as e:
            print(f"Error generating queries: {str(e)}")
            return None

    def process_query_with_perplexity(self, query):
        """Process a single query with Perplexity API"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an artificial intelligence assistant and you need to "
                        "engage in a helpful, detailed, polite conversation with a user."
                    ),
                },
                {
                    "role": "user",
                    "content": query,
                },
            ]
            
            response = self.perplexity_client.chat.completions.create(
                model="llama-3.1-sonar-large-128k-online",
                messages=messages,
            )
            
            return {
                "query": query,
                "response": response.choices[0].message.content
            }
            
        except Exception as e:
            print(f"Error processing query with Perplexity: {str(e)}")
            return None

    def synthesize_final_response(self, original_query, results):
        """Generate final comprehensive response using GPT-4"""
        try:
            # Prepare the context from all queries and responses
            context = "\n\n".join([
                f"Question: {result['query']}\nAnswer: {result['response']}"
                for result in results
            ])
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert analyst synthesizing information from multiple queries and responses. "
                        "The original question was broken down into constituent queries and follow-up questions, "
                        "each answered separately. Your task is to provide a comprehensive, insightful, and "
                        "well-structured response to the original research query, incorporating all the gathered information. "
                        "Focus on identifying key themes, relationships, and insights across the various responses. "
                        "Ensure your response is cohesive, engaging, and adds value beyond simply summarizing the "
                        "individual answers."
                    )
                },
                {
                    "role": "user",
                    "content": f"Original Query: {original_query}\n\nGathered Information:\n{context}"
                }
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error synthesizing final response: {str(e)}")
            return None

    def process_all_queries(self, research_query, max_workers=10):
        """Generate and process queries concurrently, then synthesize final response"""
        
        # Generate queries
        queries = self.generate_queries(research_query)
        if not queries:
            return None
            
        # Process queries concurrently
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_query = {
                executor.submit(self.process_query_with_perplexity, query): query 
                for query in queries
            }
            
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    print(f"Completed processing query: {query}")
                except Exception as e:
                    print(f"Error processing query '{query}': {str(e)}")
                    continue
        
        # Generate final synthesized response
        final_response = self.synthesize_final_response(research_query, results)
        
        # Return results directly without saving to file
        return {
            "original_input": research_query,
            "detailed_results": results,
            "final_response": final_response
        }
