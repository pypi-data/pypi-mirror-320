import importlib.util
import inspect
import os

import pandas as pd
from textwrap import dedent, indent

import chromadb
from .chroma_config import settings

from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor

from ...io.base import IOStream


class ToolBuilder:
    TOOL_USING_PROMPT = """# Functions
    You have access to the following functions. They can be accessed from the module called 'functions' by their function names.
For example, if there is a function called `foo` you could import it by writing `from functions import foo`
{functions}
"""

    def __init__(self, corpus_path: str, retriever=None):
        # Load the corpus (assumes tab-separated values file)
        self.df = pd.read_csv(corpus_path, sep="\t")
        
        # Clean the data: Remove any rows with NaN values in the 'document_content' column
        self.df = self.df.dropna(subset=["document_content"])
        
        # Ensure all documents are strings (if any document is not a string, convert it)
        self.df["document_content"] = self.df["document_content"].astype(str)

        document_list = self.df["document_content"].tolist()

        # Initialize ChromaDB client (non-persistent setup)
        self.db_client = chromadb.Client(settings)
        
        # Create or get the 'tool_library' collection in the ChromaDB
        self.vec_db = self.db_client.create_collection("tool_library", get_or_create=True)

        # Get the existing document IDs in the collection (to avoid duplication)
        response = self.vec_db.get()  # Get collection details

        # Handle the structure of response["documents"]
        if isinstance(response, dict) and "documents" in response:
            existing_documents = response["documents"]
            existing_ids = [str(i) for i in range(len(existing_documents))]  # Create dummy IDs based on the document list
        else:
            print("Unexpected response structure or no documents found.")
            existing_ids = []

        # Filter out documents that are already in the collection
        new_documents = [
            document_list[i] for i in range(len(document_list)) if str(i) not in existing_ids
        ]

        # Add the new documents to ChromaDB (as embeddings + metadata)
        if new_documents:
            self.vec_db.add(
                documents=new_documents,
                metadatas=[{"source": str(i)} for i in range(len(new_documents))],
                ids=[str(i) for i in range(len(new_documents))]
            )


    def retrieve(self, query: str, top_k: int = 5):
        
        iostream = IOStream.get_default()

        # Perform the query on the vector database
        results = self.vec_db.query(query_texts=[query], n_results=top_k)

        # Check if results['documents'] is a list of lists (as expected)
        if isinstance(results['documents'], list) and isinstance(results['documents'][0], list):
            documents = results['documents'][0]  # The first item is a list of documents
            distances = results['distances'][0]  # Corresponding distances for the documents
        else:
            print("Error: Unexpected result format")
            documents = []
            distances = []
        

        filtered_documents = []
        for document, distance in zip(documents, distances):
            if distance < 1.2:
                filtered_documents.append(document)
        
        # Print the filtered results
        if filtered_documents:
            for document in filtered_documents:
                iostream.print(f"==> Suitable tool available for '{query}'")
                iostream.print(document)
            iostream.print("\n", "-" * 80, flush=True, sep="")
        else:
            pass

        return filtered_documents
    
    
    def bind(self, agent: AssistantAgent, functions: str):
        """Binds the function to the agent so that the agent is aware of it."""
        sys_message = agent.system_message
        sys_message += self.TOOL_USING_PROMPT.format(functions=functions)
        agent.update_system_message(sys_message)
        return


    def bind_user_proxy(self, agent: UserProxyAgent, tool_root: str):
        """
        Updates user proxy agent with an executor so that code executor can successfully execute function-related code.
        Returns an updated user proxy.
        """
        # Find all the functions in the tool root
        functions = find_callables(tool_root)

        code_execution_config = agent._code_execution_config
        executor = LocalCommandLineCodeExecutor(
            timeout=code_execution_config.get("timeout", 180),
            work_dir=code_execution_config.get("work_dir", "coding"),
            functions=functions,
        )
        code_execution_config = {
            "executor": executor,
            "last_n_messages": code_execution_config.get("last_n_messages", 1),
        }
        updated_user_proxy = UserProxyAgent(
            name=agent.name,
            is_termination_msg=agent._is_termination_msg,
            code_execution_config=code_execution_config,
            human_input_mode="NEVER",
            default_auto_reply=agent._default_auto_reply,
        )
        return updated_user_proxy


def get_full_tool_description(py_file):
    """
    Retrieves the function signature for a given Python file.
    """
    with open(py_file, "r") as f:
        code = f.read()
        exec(code)
        function_name = os.path.splitext(os.path.basename(py_file))[0]
        if function_name in locals():
            func = locals()[function_name]
            content = f"def {func.__name__}{inspect.signature(func)}:\n"
            docstring = func.__doc__

            if docstring:
                docstring = dedent(docstring)
                docstring = '"""' + docstring + '"""'
                docstring = indent(docstring, "    ")
                content += docstring + "\n"
            return content
        else:
            raise ValueError(f"Function {function_name} not found in {py_file}")


def find_callables(directory):
    """
    Find all callable objects defined in Python files within the specified directory.
    """
    callables = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                module_name = os.path.splitext(file)[0]
                module_path = os.path.join(root, file)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for name, value in module.__dict__.items():
                    if callable(value) and name == module_name:
                        callables.append(value)
                        break
    return callables
