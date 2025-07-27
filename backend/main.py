#for fastapi backend
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import return_response
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #TO DO - change during production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message : str
    video_id:str


@app.post("/chat")
def chat_api(msg:Message):
    print(f"Received message: {msg.message} for video ID: {msg.video_id}")
    try:
        res = return_response(msg.message, msg.video_id)
        return {"response":f"{res}"}
    except Exception as e:
        return {"response": f"An error occurred: {e}"}

if __name__ == "__main__":
    import uvicorn
    print("Server is running on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
    print("Server stopped.")
