from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Database.DataBaseInterface import DataBaseInterface

app = FastAPI(title = "LapAgent Backend",version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
db=DataBaseInterface()

@app.get("/")
async def root():
    return {"message": "Hello World\n"}

@app.post("/receive_message")
async def receive_message(request: dict):
    user_message = request.get("message")
    #print(f"Received message: {user_message}")
    db.store(user_message)
    return {"reply":user_message}