from abc import ABC
from langchain_core.messages import ToolMessage
from langchain.schema.agent import AgentFinish
from langgraph.prebuilt import ToolInvocation, ToolExecutor

from llm_foundation import logger

# def route(result):
#     if isinstance(result, AgentFinish):
#         return result.return_values['output']
#     else:
#         tools = {
#             "search_wikipedia": search_wikipedia, 
#             "get_current_temperature": get_current_temperature,
#         }
#         return tools[result.tool].run(result.tool_input)


class ToolMaster(ABC):
    
    def __init__(self, available_tools):
        self.tool_executor = ToolExecutor(available_tools)
    
    # Define the function to execute tools
    def pre_call_tool(self, state):
        logger.info("-------------- Pre Call Tool ---------------")
        messages = state["messages"]
        # Based on the continue condition
        # we know the last message involves a function call
        last_message = messages[-1]
        # We construct an ToolInvocation from the function_call
        return last_message
        
    def post_call_tool(self, state, responses):
        logger.info("-------------- Post Call Tool ---------------")
        tool_messages = []
        for response in responses:
            tool_call_id, tool_name, response = response
            tool_message = ToolMessage(
                content=str(response), name=tool_name, tool_call_id=tool_call_id
            )
            tool_messages.append(tool_message)

        return {
            "last_node": "call_tools",
            "messages": tool_message,  # We return a list, because this will get added to the existing list of messages
        }

        
    def _call_tool(self, tool_call_definition):
        logger.info("-------------- Call Tool ---------------")
        action = ToolInvocation(
            tool=tool_call_definition["name"],
            tool_input=tool_call_definition["args"],
        )
        # We call the tool_executor and get back a response
        logger.info(action)
        print("OOFOOOSFOfs")
        response = self.tool_executor.invoke(action)
        logger.info(f"Response ({type(response)}): {response}")
        logger.info("-------------- End Call Tool ---------------")
        return (tool_call_definition["id"], tool_call_definition["name"], response)


    def call_tools(self, message):
        responses = []
        for tool_call_definition in message.tool_calls:
            # add tuples of (tool_call_id, tool_name, response)
            responses.append(self._call_tool(tool_call_definition))
        return responses


    def agentic_call_tool(self, state):
        message = self.pre_call_tool(state)
        responses = self.call_tools(message)
        return self.post_call_tool(state, responses)
        