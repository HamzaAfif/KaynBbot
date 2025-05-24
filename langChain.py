from langchain_community.utilities import SQLDatabase
import os
from dotenv import load_dotenv
import re

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key # type: ignore

db = SQLDatabase.from_uri("sqlite:///easyfind.db")



########## Convert question to SQL query :

from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
#chain = create_sql_query_chain(llm, db)
#response = chain.invoke({"question": "How many clients are there"})

def format_user_confirmation_text(user_confirmation_text):
    
    formatted_text = re.sub(r'\s+', ' ', user_confirmation_text.strip())
    return formatted_text

def generate_sql_query(user_confirmation_text):
    # Format the user confirmation text before invoking the SQL query chain
    formatted_text = format_user_confirmation_text(user_confirmation_text)

    # Create a dictionary input for the chain invoke method with the required key
    input_data = {
        "question": formatted_text  # Ensure this matches what your chain expects
    }
    
    chain = create_sql_query_chain(llm, db)
    response = chain.invoke(input_data)  # Pass the dictionary with the 'question' key
    
    return response

    
#print(response)
#print(db.run(response))

if __name__ == "__main__": 

    ########## Execute SQL query :

    from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

    execute_query = QuerySQLDataBaseTool(db=db)
    write_query = create_sql_query_chain(llm, db)
    #chain = write_query | execute_query
    #reply = chain.invoke({"question": "How many clients are there"})
    #print(reply)


    ########## Answer the question :

    from operator import itemgetter

    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import PromptTemplate
    from langchain_core.runnables import RunnablePassthrough

    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )

    answer = answer_prompt | llm | StrOutputParser()
    chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )
        | answer
    )
    
    #answer = chain.invoke({"question": "How many clients are there"})
    #print(answer)

    ########## Use Agents : 

    from langchain_community.agent_toolkits import create_sql_agent 

    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

    answer = agent_executor.invoke(
        {
            "input": "List the total clients per address. how many client there are?"
        }
    )


    
        