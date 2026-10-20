from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Database.DataBaseInterface import DataBaseInterface
from Agent.agent import Agent
from public.AI_configure import base_url_dict

from public.logger import setup_logger
logger = setup_logger(__name__)

app = FastAPI(title = "LapAgent Backend",version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
db=DataBaseInterface()
agent=Agent()

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
    feedback = agent.interact(user_message)

    sys_package ={
        "message": feedback,
        "conversation_id": user_package.get("conversation_id"),
        "role_id": db.check_role("system"),
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
    model_list = agent.get_model_list()
    return {"models": model_list}

@app.get("/get_base_list")
async def get_able_providers():
    base_list = list(base_url_dict.keys())
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

@app.post("/start_conversation")
async def start_conversation(request: dict):
    model_name = request.get("message")
    if not model_name:
        logger.warning("No model set. Please set a model first.")
        return {"error": "No model set. Please set a model first."}
    conversation_id = db.new_conversation(model_name)
    return {"reply": conversation_id}

@app.post("/load_conversation")
async def load_conversation(request:dict):
    conversation_id = request.get("message")
    if not conversation_id:
        logger.warning("No conversation ID provided.")
        return {"error": "No conversation ID provided."}
    return {"reply": db.load_conversation(conversation_id)}

@app.post("/check_role")
async def check_role(request:dict):
    role_name = request.get("message")
    if not role_name:
        logger.warning("No role name provided.")
        return {"error": "No role name provided."}
    return {"reply": db.check_role(role_name)}
@app.post("/check_role_name")
async def check_role_name(request:dict):
    role_id = request.get("message")
    if not role_id:
        logger.warning("No role ID provided.")
        return {"error": "No role ID provided."}
    return {"reply": db.check_role_name(role_id)}

@app.post("/delete_conversation")
async def delete_conversation(request: dict):
    conversation_id = request.get("message")
    if not conversation_id:
        logger.warning("No conversation ID provided.")
        return {"error": "No conversation ID provided."}
    db.del_conversation(conversation_id)
    return {"reply": f"Conversation {conversation_id} deleted successfully."}