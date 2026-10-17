from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Database.DataBaseInterface import DataBaseInterface
from Agent.agent import Agent
from Agent import base_url_dict

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
    user_message = request.get("message")
    #print(f"Received message: {user_message}")
    db.store(user_message)
    feedback = agent.interact(user_message)
    db.store(feedback)
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