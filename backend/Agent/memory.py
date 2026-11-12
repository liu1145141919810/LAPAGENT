from typing import Any, Dict, List
from hindsight_client import Hindsight
import os

from public.logger import setup_logger
logger = setup_logger(__name__)

class MemoryAdapter:
    def __init__(self):
        #This environment configuration work is finished here!
        hindsight_api_key = os.getenv("HINDSIGHT_API_KEY")
        hindsight_base_url = os.getenv("HINDSIGHT_BASE_URL")
        self.hindsightmemory = HindsightMemory(
            api_key=hindsight_api_key,
            base_url=hindsight_base_url,
        )
    async def store_memory(self):
        pass
    async def load_memory(self):
        pass
    async def reflect_t
            logger.info("HindsightMemory initialized successfully")he_memory(self):
        pass

class HindsightMemory():
    def __init__(
            self,
            bank_id : str=None,
            base_url : str=None,
            api_key : str=None,
            timeout : float=60.0,
        ):
        self.bank_id = bank_id
        self.client = Hindsight(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout
        )

    async def recall(
            self,
            query:str,
        ):
        result = await self.client.arecall(
            bank_id = self.bank_id,
            query = query
        )
        return [
            {
                "text": memory.text,
                "type": memory.type
            }for memory in result.results
        ]
    
    async def reflect(
            self,
            query:str,
            context:str=None,
        ):
        result = await self.client.areflect(
            bank_id=self.bank_id,
            query=query,
            context=context
        )
        return result.text

    async def retain(
            self,
            content:str,
            context:str=None
        ) -> Dict[str,Any]:
        result = await self.client.aretain(
            bank_id = self.bank_id,
            content = content,
            context = context,
        )
        return {
            "success":result.success,
            "bank_id": self.bank_id,
            "items_count":result.items_count
        }