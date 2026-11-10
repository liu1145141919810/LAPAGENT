from typing import Any,Dict
import asyncio

from public.logger import setup_logger
logger = setup_logger(__name__)
from Webcrawl.webcrawl import WebCrawl

class AgentToolBox:
    def __init__(self,db,redis):
        self.db = db
        self.redis = redis
        self.web_crawl = WebCrawl()
        self.handlers={
            "load_current_history": self.load_current_history,
            "load_memory": self.load_memory,
            "save_memory": self.save_memory,
            "search_the_Internet": self.search_the_Internet
        }
        self.backinfo={
            "conversation_id": None,
            "test_box":{
                "load_current_history": None,
                "load_memory": None,
                "save_memory": None,
                "search_the_Internet": None
            },
        }

    async def call(self,tool_name:str,**lwargs:Any) -> Dict[str,Any]:
        if tool_name not in self.handlers:
            logger.error(f"Tool {tool_name} not found in handlers")
            return {
                "status": "error",
                "data":{},
                "message": f"Tool {tool_name} not found"
            }
        handler = self.handlers[tool_name]
        if asyncio.iscoroutinefunction(handler):
            msg = await handler(**lwargs)
        else:
            msg = handler(**lwargs)

        if isinstance(msg, dict) and "error" in msg:
            return {
                "status": "error",
                "data": msg,
                "message": msg["error"]
            }
        return {
            "status": "success",
            "data": msg,
            "message": "ok"
        }
    
    def tool_definitions(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "load_current_history",
                    "description": "Return the history information about the current conversation session",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "load_memory",
                    "description": "Load several key information the user wants the model to remember",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_memory",
                    "description": "Save key information the user wants the model to remember",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "memory": {"type": "string"}
                        },
                        "required": ["memory"]
                    }
                }
            },
            {
                "type": "function",
                "function":{
                    "name": "search_the_Internet",
                    "description":"Return back the search results from the Internet",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "max_results":{
                                "type": "integer",
                                "description": "Maximum number of search results to return",
                                "minimum": 1,
                                "maximum": 5,
                                "default": 5,
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    def __set(self, tool_name: str) -> None:
        self.backinfo["test_box"][tool_name] = True
    #========= Following is the Area for the actual execution of the tools =========
    def load_current_history(self, **kwargs: Any) -> Dict[str, Any]:
        self.__set("load_current_history")

        id = self.backinfo.get("conversation_id")
        if not id:
            logger.error("No conversation ID found in backinfo")
            # Some feedback for none ID
            return {"error": "No conversation ID found"}
        messages = self.db.load_conversation(id)
        messages = messages[-max(10,len(messages)):]  # Keep at least the last 10 messages
        return messages
           
    def save_memory(self, **kwargs: Any) -> Dict[str, Any]:
        self.__set("save_memory")

        memory = kwargs.get("memory")
        if not memory:
            logger.error("No memory provided")
            return {"error": "No memory provided"}
        self.db.store_memory(memory)
        return {"status": "success"}

    async def load_memory(self, **kwargs: Any) -> Dict[str, Any]:
        self.__set("load_memory")

        cache_key = "memory"
        memories = await self.redis.get_cache(cache_key) 

        if memories is not None:
            return {"memories": memories}
        logger.warning("No memories found in cache, checking database/Redis")
        memories = self.db.check_memory()
        if memories is not None:
            await self.redis.set_cache(cache_key, memories)
        return {"memories": memories}

    async def search_the_Internet(self, **kwargs: Any) -> Dict[str, Any]:
        self.__set("search_the_Internet")

        query = kwargs.get("query")
        max_results = kwargs.get("max_results", 5)

        if not isinstance(query, str) or not query.strip():
           return {"error": "A non-empty query is required"}
        if len(query.strip())>500:
            return {"error": "Query length exceeds 500 characters"}
        if not isinstance(max_results, int) or max_results < 1 or max_results > 5:
            return {"error": "max_results must be an integer between 1 and 5"}

        return await self.web_crawl.search(
            query=query.strip(),
            max_results=max_results
        )