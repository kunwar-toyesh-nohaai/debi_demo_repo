"""Web-friendly agent loop that doesn't use terminal confirmations."""

import logging
import os
import uuid
import asyncio
import concurrent.futures
from contextvars import ContextVar
from langchain.agents import create_react_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from typing import List, Optional
from difflib import unified_diff

from tools.file_tools import list_directory, read_file, write_file
from tools.git_tools import run_git_command, commit_changes as _commit_changes
from prompts import SYSTEM_PROMPT

# Set up logger
logger = logging.getLogger("agent_debugger")

# Track which files have been modified during a run
APPLIED_FILE_CHANGES: List[str] = []

# Context variables to pass manager and websocket to tools running in threads
context_manager: ContextVar = ContextVar('context_manager', default=None)
context_websocket: ContextVar = ContextVar('context_websocket', default=None)
context_loop: ContextVar = ContextVar('context_loop', default=None)


def _record_file_change(file_path: str):
    """Record that a file has been modified."""
    global APPLIED_FILE_CHANGES
    if file_path not in APPLIED_FILE_CHANGES:
        APPLIED_FILE_CHANGES.append(file_path)


def get_applied_file_changes():
    """Return a copy of the list of modified files."""
    return list(APPLIED_FILE_CHANGES)


def reset_applied_file_changes():
    """Clear the list of recorded file changes."""
        logger.error(f"Failed to write file: {filepath}")
    
    return result


def commit_changes_wrapper_web(commit_message: str) -> str:
    """
    Web-friendly wrapper for commit_changes that doesn't ask for confirmation.
    
    Args:
        commit_message: The commit message.
        
    Returns:
        Result from commit_changes function.
    """
    logger.info(f"Auto-committing with message: {commit_message}")
    result = _commit_changes(commit_message)
    logger.info(f"Commit result: {result}")
    return result


def create_tools_web():
    """
    Create and return a list of tools for the web agent (without confirmations).
    
    Returns:
        List of Tool objects that the agent can use.
    """
    tools = [
        Tool(
            name="list_directory",
            func=list_directory,
            description="List files and directories in the specified path. Input should be a directory path (e.g., '.' for current directory, or 'src' for a subdirectory)"
        ),
        Tool(
            name="read_file",
            func=read_file,
            description="Read the contents of a file. Input should be the file path relative to current directory"
        ),
        Tool(
            name="write_file",
            func=write_file_wrapper_web,
            description="""Write content to a file. Input should be formatted exactly as:
FILEPATH: path/to/file
ISSUE SUMMARY:
Brief explanation of why this change is needed
CONTENT:
<actual file content here>

The file will be created if it doesn't exist, or overwritten if it does."""
        ),
        Tool(
            name="run_git_command",
            func=run_git_command,
            description="Run a git command. Input should be the git command and arguments (e.g., 'status', 'log -n 5', 'diff')"
        ),
        Tool(
            name="commit_changes",
            func=commit_changes_wrapper_web,
            description="Commit all changes with a commit message. Input should be the commit message"
        ),
    ]
    
    return tools


def create_agent_web(api_key: str):
    """
    Create and initialize the LangChain agent for web use (no confirmations).
    
    Args:
        api_key: Google API key for Gemini.
        
    Returns:
        Initialized LangChain AgentExecutor.
    """
    from langchain import hub
    from langchain_core.prompts import PromptTemplate
    
    logger.info("Creating web agent (no confirmations)...")
    
    # Create the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=api_key,
        temperature=0,
        convert_system_message_to_human=True
    )
    
    # Create tools
    tools = create_tools_web()
    
    # Add web-specific instructions to system prompt
    web_instructions = """

IMPORTANT WEB MODE INSTRUCTIONS:
- You are running in web mode through a chat interface
- File changes will be applied automatically WITHOUT confirmation
- Git commits will be made automatically WITHOUT confirmation  
- Always explain what you're doing before making changes
- Provide clear summaries of changes made
- Be concise but thorough in your responses
"""
    
    enhanced_system_prompt = SYSTEM_PROMPT + web_instructions
    
    # Try to pull the standard ReAct prompt from LangChain hub, fallback to custom
    try:
        logger.debug("Attempting to pull standard ReAct prompt from LangChain hub")
        prompt = hub.pull("hwchase17/react")
        # Add system prompt to the beginning
        prompt = prompt.partial(system_message=enhanced_system_prompt)
        logger.debug("Using standard ReAct prompt from hub")
    except Exception as e:
        logger.warning(f"Could not pull prompt from hub: {e}, using custom prompt")
        # Create a custom prompt template for ReAct agent with system message
        prompt = PromptTemplate.from_template("""{system_message}

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}""").partial(system_message=enhanced_system_prompt)
    
    # Create agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create executor with more lenient settings
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=15,
        max_execution_time=300,
        handle_parsing_errors=True,
        return_intermediate_steps=False
    )
    
    logger.info("Web agent created successfully")
    return agent_executor


def run_agent_web(agent: AgentExecutor, bug_description: str) -> str:
    """
    Run the web agent with a bug description.
    
    Args:
        agent: The initialized LangChain AgentExecutor.
        bug_description: Description of the bug to debug.
        
    Returns:
        Agent's response as a string.
    """
    logger.info("Running web agent...")
    logger.debug(f"Bug description: {bug_description}")
    
    try:
        result = agent.invoke({"input": bug_description})
        output = result.get("output", "")
        
        logger.info("Web agent execution completed successfully")
        logger.debug(f"Agent output length: {len(output)} characters")
        
        return output
        
    except Exception as e:
        error_msg = f"Error during web agent execution: {str(e)}"
        logger.exception(error_msg)
        return f"I encountered an error while processing your request: {str(e)}\n\nPlease try rephrasing your request or providing more details."
