from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from sentence_transformers import CrossEncoder
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.retrievers import WikipediaRetriever
from Backend.app.Retrieving import create_retriever
import re
import json
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
api_key = os.getenv('GOOGLE_API_KEY')


#--------------------Nested Query------------------------------


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts the first JSON object found in a string using regex.
    """
    # Regex to find a JSON object starting with { and ending with }
    # Uses re.DOTALL to allow '.' to match newline characters.
    # This assumes the JSON object is the main content between the first { and last }
    match = re.search(r'\{.*\}', text, re.DOTALL)

    if match:
        potential_json = match.group(0)
        try:
            # Attempt to parse the extracted string as JSON
            parsed_json = json.loads(potential_json)
            # Ensure it's actually an object (dictionary)
            if isinstance(parsed_json, dict):
                return parsed_json
            else:
                 print(f"Warning: Extracted JSON is not an object (dict): {type(parsed_json)}")
                 return None # Or handle arrays/other types if needed
        except json.JSONDecodeError:
            # Handle cases where the extracted text is not valid JSON
            print(f"Error: Failed to decode JSON from extracted text: {potential_json}")
            return None
    else:
        # No pattern matching '{...}' found
        print("No JSON object pattern found in the text.")
        return None

def get_aggregated_query(queries: str, current_question: str):
    """
    Get the restructured query from the previous queries and current question.
    """
    prompt = PromptTemplate(
        template="""
        You are given a list of previously asked questions and a recently asked question. Your task is to analyze and combine all questions into a single, concise, and coherent question that captures the full intent and context provided across them.

The final question should preserve the core meaning of each input question.

Use pronoun resolution to replace ambiguous references like "this", "that" or "it" with the correct noun.

Assume all questions are about the same underlying subject unless otherwise stated.

Return the aggregated question in a JSON format with the key "aggregated_question".

If the the recently asked question is of different subject then, return the recently asked question as it is in the "aggregated_question".

Example Inputs:

**Previously Asked Questions**
1. What is B2B model?

**Recently Asked Question**
How is it different from B2C Model?

**Output**:
{{
    "aggregated_question": "What are the differences between B2B and B2C models?"
}}

**Previously Asked Questions**
1. What is statistical analysis?
2. Give it for a 5 marks answer.

**Recently Asked Question**
Explain second step in detail

**Output**:
{{
    "aggregated_question": "Give explanation of second step in statistical analysis for a 5 marks answer."
}}

**Previously Asked Questions**
{previous_questions}

**Recently Asked Question**
{current_question}

**Final Answer**
""",
        input_variables=["previous_questions", "current_question"]
    )
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", temperature=0.2, groq_api_key=GROQ_API_KEY
    )

    chain = prompt | llm
    response = chain.invoke(
        {"previous_questions": queries, "current_question": current_question}
    )

    json_data = extract_json_object(response.content)

    if json_data and "aggregated_question" in json_data:
        return json_data["aggregated_question"]
    else:
        # Fallback or error handling if JSON extraction fails
        print(f"Warning: Could not extract aggregated question from LLM response: {response.content}")
        # Fallback to using the current question directly or raise an error
        return current_question
    
#--------------------- Ensemble Retriever and Cross Encoder -------------------------


def get_required_context(agg_query):
    ensemble_retriever = create_retriever()

    results = ensemble_retriever.get_relevant_documents(agg_query)
    rerank_pairs = [(agg_query, doc.page_content) for doc in results]

    scores = model.predict(rerank_pairs)

    # print(scores)

    ranked_results = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)
    # print(ranked_results)

    top_10_contents = [doc.page_content for _, doc in ranked_results[:10]]
    # print(top_10_contents)
   

    contents=[]
    for i in top_10_contents:
        if "Chunk_Text:" in i:
            j=i[12:].lstrip()
            contents.append(j)
        else:
            contents.append(i)

    # for i in top_10_contents:
    #     print(i)
   
    # for i in contents:
    #     print(i)
   
    # print(len(contents))
    # print(len(top_10_contents))

    joined_content = "\n\n".join(contents)
    # print(joined_content)
    return joined_content

def get_llm_response(context, query, history):
    prompt = PromptTemplate(
        input_variables=["query", "retrieved_text"],
        template="""
        A user asked the following query:

        "{query}"

        The following documents were retrieved from a knowledge base to help answer this query:

        {retrieved_text}

        **Chat History:**
        {chat_history}

        Based on the retrieved information, provide a comprehensive, refined, and insightful response to the user's query.
        """

    )

    # Load the LLM (customize as needed)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17", temperature=0.2, api_key=api_key)

    # Create chain and run
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({"query": query, "retrieved_text": context, "chat_history": history})
    # print(response)
    return response

#----------------For Wiki Search---------------------
def get_wikipedia_context(query):
    """
    Get relevant context from Wikipedia.
    """
    retriever = WikipediaRetriever()
    docs = retriever.invoke(query)
    wiki = [doc.page_content for doc in docs]
    print("Wiki searched")
    print("Doc length: ", len(docs))
    print(docs)
    return wiki



if __name__ == "__main__":
    queries = """1. What is B2B model?
    2. What is B2C model"""

    query = "How do both differ from each other"
    agg_query = get_aggregated_query(queries, query)
    context = get_required_context(agg_query)
    response = get_llm_response(context, agg_query)

    print(response)












