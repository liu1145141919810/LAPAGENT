from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from Database.DataBaseInterface import DataBaseInterface
from Agent.agent import Agent
from public.AI_configure import base_url_dict
from public.logger import setup_logger
logger = setup_logger(__name__)
from Redis.redis_client import RedisManager

cors_origins_env = os.getenv("LAPAGENT_CORS_ORIGINS", "http://localhost:5173")
cors_origins = [origin.strip() for origin in cors_origins_env.split(',') if origin.strip()]

db=DataBaseInterface()
agent=Agent(db)
redis_manager = RedisManager()

app = FastAPI(
    title = "LapAgent Backend",
    version="0.1.0",
    lifespan=redis_manager.lifespan
    )
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

#=========Area for Address Functions=========//
@app.get("/")
async def root():
    return {"message": "Hello World\n"}
#Converted it into a structure both have receive and transmit
@app.post("/receive_message")
async def receive_message(request: dict):
    logger.info("Activated receive_message endpoint")

    user_package = request.get("message")
    logger.info(f"Received message: {user_package}")
    db.store_message(user_package)
    user_message = user_package.get("message")

    logger.info(f"User message received: {user_message}")
    feedback = agent.session_interact(user_message)

    sys_package ={
        "message": feedback,
        "conversation_id": user_package.get("conversation_id"),
        "role_id": db.check_role("agent"),
    }
    db.store_message(sys_package)
    return {"reply": feedback}

@app.post("/set_api_key")
async def set_api_key(request: dict):
    #print(f"Received API key: {request.get('message')}")
    api_key = request.get("message")
    agent.set_API_key(api_key)
    return {"message": "API key set successfully"}

@app.get("/get_model_list")
async def get_able_models():
    # Test it now for the Redis 
    cache_key = "model_list"
    cached_model_list = await redis_manager.get_cache(cache_key)
    if cached_model_list is not None:
        return {"models": cached_model_list}
    model_list = agent.get_model_list()
    await redis_manager.set_cache(cache_key, model_list)
    return {"models": model_list}

@app.get("/get_base_list")
async def get_able_providers():
    cache_key = "base_list"
    cached_base_list = await redis_manager.get_cache(cache_key)
    if cached_base_list is not None:
        return {"bases": cached_base_list}
    base_list = list(base_url_dict.keys())
    await redis_manager.set_cache(cache_key, base_list)
    return {"bases": base_list}

@app.post("/set_model")
async def set_model(request: dict):
    model = request.get("message")
    agent.set_model(model)
    return {"message": "Model set successfully"}

@app.get("/load_history")
async def load_history():
    logger.info("Loading conversation history...")
    return db.all_history()

@app.get("/get_agent_provider")
async def get_agent_provider():
    cache_key = "agent_provider"
    cached_provider = await redis_manager.get_cache(cache_key)
    if cached_provider is not None:
        return {"provider": cached_provider}
    provider = agent.read_provider()
    await redis_manager.set_cache(cache_key, provider)
    return {"provider": str(provider)}

@app.post("/start_conversation")
async def start_conversation(request: dict):
    model_name = request.get("message")
    if not model_name:
        if not agent.read_model():
            logger.warning("No model set. Please set a model first.")
            return {"error": "No model set. Please set a model first."}
    conversation_id = db.new_conversation(model_name)
    agent.set_tool_conversation_id(conversation_id)
    logger.info(f"Started new conversation with ID: {conversation_id}")
    return {"reply": conversation_id}

@app.post("/load_conversation")
async def load_conversation(request:dict):
    conversation_id = request.get("message")
    if not conversation_id:
        logger.warning("No conversation ID provided.")
        return {"error": "No conversation ID provided."}
    agent.set_tool_conversation_id(conversation_id)
    return {"reply": db.load_conversation(conversation_id)}

@app.post("/check_role")
async def check_role(request:dict):
    role_name = request.get("message")
    cache_key = f"role:{role_name}"
    cached_role = await redis_manager.get_cache(cache_key)
    if cached_role is not None:
        return {"reply": cached_role}
    if not role_name:
        logger.warning("No role name provided.")
        return {"error": "No role name provided."}
    role = db.check_role(role_name)
    await redis_manager.set_cache(cache_key, role)
    return {"reply": role}

@app.post("/check_role_name")
async def check_role_name(request:dict):
    # Test it now for the Redis cache
    role_id = request.get("message")
    if not role_id:
        logger.warning("No role ID provided.")
        return {"error": "No role ID provided."}
    cache_key = f"role_name:{role_id}"
    cached_role_name = await redis_manager.get_cache(cache_key)
    if cached_role_name is not None:
        return {"reply": cached_role_name}
    role_name = db.check_role_name(role_id)
    await redis_manager.set_cache(cache_key, role_name)
    return {"reply": role_name}

@app.post("/delete_conversation")
async def delete_conversation(request: dict):
    conversation_id = request.get("message")
    if not conversation_id:
        logger.warning("No conversation ID provided.")
        return {"error": "No conversation ID provided."}
    db.del_conversation(conversation_id)
    return {"reply": f"Conversation {conversation_id} deleted successfully."}