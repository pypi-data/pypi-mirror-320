from typing import Any, Dict, List, Optional, Tuple, Union

from autogen import Agent, ConversableAgent, UserProxyAgent

from .falkor_graph_query_engine import FalkorGraphQueryEngine
from .graph_query_engine import GraphStoreQueryResult
from .graph_rag_capability import GraphRagCapability

class FalkorGraphRagCapability(GraphRagCapability):
    """
    The FalkorDB GraphRAG capability integrates FalkorDB with graphrag_sdk version: 0.1.3b0.
    """

    def __init__(self, query_engine: FalkorGraphQueryEngine):
        """
        Initialize GraphRAG capability with a graph query engine.
        Args:
            query_engine: An instance of FalkorGraphQueryEngine for querying the database.
        """
        self.query_engine = query_engine

    def add_to_agent(self, agent: ConversableAgent):
        """
        Adds FalkorDB GraphRAG capability to the given agent.
        """

        # Ensure agents is a list, even if a single agent is passed
        if not isinstance(agent, list):
            agent = [agent]

        for single_agent in agent:
            try:
                self.graph_rag_agent = single_agent

                # Register a hook to process the last received message.
                single_agent.register_hook(
                    hookable_method="process_last_received_message",
                    hook=self.process_last_received_message
                )

                # Ensure the agent has a valid system message.
                if not single_agent.system_message:
                    single_agent.update_system_message("You are now equipped with the ability to retrieve data from FalkorDB.")
        
            except Exception as e:
                # Catch errors and skip this agent.
                continue  # Skip this agent and move to the next one

    def process_last_received_message(self, text: Union[Dict, str]):
        """
        Integrates FalkorDB query results into the agent's response process.
        Queries FalkorDB based on the received message and appends relevant data.
    
        Args:
            text: The incoming message to process.
        Returns:
            The modified message with FalkorDB results appended.
        """
        try:
            # Retrieve the question from the message context.
            if isinstance(text, str):
                question = text
            elif isinstance(text, dict) and "content" in text:
                question = text["content"]
            else:
                raise ValueError("Invalid message format. Must be a string or a dict with 'content' key.")

            # Query FalkorDB using the extracted question.
            result: GraphStoreQueryResult = self.query_engine.query(question)

            # Append the FalkorDB result to the message.
            falkor_response = result.answer if result.answer else "No relevant data found in FalkorDB."
            if isinstance(text, str):
                return f"{text}\n\nFalkorDB Reference: {falkor_response}"
            else:
                text["content"] += f"\n\nFalkorDB Reference: {falkor_response}"
                return text

        except Exception as e:
            # Log the error and return the original text with an error message.
            error_message = f"Error while retrieving data from FalkorDB: {e}"
            if isinstance(text, str):
                return f"{text}\n\n{error_message}"
            else:
                text["content"] += f"\n\n{error_message}"
                return text

    def _reply_using_falkordb_query(
        self,
        recipient: ConversableAgent,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """
        Query FalkorDB and return the message. Internally, it utilises OpenAI to generate a reply based on the given messages.
        The history with FalkorDB is also logged and updated.

        The agent's system message will be incorporated into the query, if it's not blank.

        If no results are found, a default message is returned: "I'm sorry, I don't have an answer for that."

        Args:
            recipient: The agent instance that will receive the message.
            messages: A list of messages in the conversation history with the sender.
            sender: The agent instance that sent the message.
            config: Optional configuration for message processing.

        Returns:
            A tuple containing a boolean indicating success and the assistant's reply.
        """
        # question = self._get_last_question(messages[-1])
        question = self._messages_summary(messages, recipient.system_message)
        result: GraphStoreQueryResult = self.query_engine.query(question)

        return True, result.answer if result.answer else "I'm sorry, I don't have an answer for that."

    def _messages_summary(self, messages: Union[Dict, str], system_message: str) -> str:
        """Summarize the messages in the conversation history. Excluding any message with 'tool_calls' and 'tool_responses'
        Includes the 'name' (if it exists) and the 'content', with a new line between each one, like:
        customer:
        <content>

        agent:
        <content>
        """

        if isinstance(messages, str):
            if system_message:
                summary = f"IMPORTANT: {system_message}\nContext:\n\n{messages}"
            else:
                return messages

        elif isinstance(messages, List):
            summary = ""
            for message in messages:
                if "content" in message and "tool_calls" not in message and "tool_responses" not in message:
                    summary += f"{message.get('name', '')}: {message.get('content','')}\n\n"

            if system_message:
                summary = f"IMPORTANT: {system_message}\nContext:\n\n{summary}"

            return summary

        else:
            raise ValueError("Invalid messages format. Must be a list of messages or a string.")