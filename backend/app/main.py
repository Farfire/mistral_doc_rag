from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mistralai import Mistral
import os
from dotenv import load_dotenv
import httpx
import app.function_calling_tools as tools
import json

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Mistral AI Chat API",
    description="API pour interagir avec Mistral AI",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Mistral client
mistral_api_key = os.getenv("MISTRAL_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
if not mistral_api_key:
    raise ValueError("MISTRAL_API_KEY environment variable is not set")
client = Mistral(api_key=mistral_api_key)


class ChatRequest(BaseModel):
    message: str
    model: str = "mistral-large-latest"


class ChatResponse(BaseModel):
    response: str


@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API Mistral AI Chat",
        "documentation": "/docs",
        "endpoints": {"chat": "/api/chat", "models": "/api/models"},
    }


# Store conversation history in memory
conversation_history = []


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Add user message to history
        conversation_history.append({"role": "user", "content": request.message})

        # Get response from Mistral with full conversation history
        chat_response = client.chat.complete(
            model=request.model,
            messages=conversation_history,
            tools=tools.tools,
            tool_choice="auto",
            parallel_tool_calls=False,
        )

        # Ajoute la réponse assistant AVEC les tool_calls dans l'historique
        conversation_history.append(
            {
                "role": "assistant",
                "tool_calls": chat_response.choices[0].message.tool_calls,
                "content": chat_response.choices[0].message.content,  # optionnel
            }
        )

        tool_calls = chat_response.choices[0].message.tool_calls
        if tool_calls:
            print(f"Number of tool calls: {len(tool_calls)}")
            tool_call = tool_calls[0]
            function_name = tool_call.function.name
            function_params = json.loads(tool_call.function.arguments)
            print(
                "\nfunction_name: ",
                function_name,
                "\nfunction_params: ",
                function_params,
            )

            function_result = tools.names_to_functions[function_name](**function_params)
            # print('function_result', function_result)
            print("-" * 50)

            conversation_history.append(
                {
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_result),
                    "tool_call_id": tool_call.id,
                }
            )

            chat_response = client.chat.complete(
                model=request.model, messages=conversation_history
            )

            conversation_history.pop()
            conversation_history.pop()

        conversation_history.append(
            {"role": "assistant", "content": chat_response.choices[0].message.content}
        )

        return ChatResponse(response=conversation_history[-1]["content"])
    except Exception as e:
        print("----")
        print(e)
        print("----")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def get_models():
    try:
        models = client.models.list()
        return {"models": [model.id for model in models.data]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reset")
async def reset_conversation():
    try:
        # Réinitialiser le client Mistral
        global conversation_history
        conversation_history = []
        return {"status": "success", "message": "Conversation réinitialisée"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weather")
async def get_weather(latitude: float, longitude: float):
    try:
        url = f"https://weather.googleapis.com/v1/currentConditions:lookup"

        params = {
            "key": google_api_key,
            "location.latitude": latitude,
            "location.longitude": longitude,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
