from fastapi import FastAPI, HTTPException
from typing import Optional, Dict, List
from ..assistant import Assistant

def create_fastapi_app(assistant: Assistant) -> FastAPI:
    """
    Create a FastAPI app for the given assistant.

    Args:
        assistant (Assistant): The assistant instance for which the API is being created.

    Returns:
        FastAPI: A FastAPI app with endpoints for interacting with the assistant.
    """
    app = FastAPI()

    @app.post("/chat")
    async def chat(message: str):
        """
        Endpoint to interact with the assistant.
        """
        # Use the assistant's print_response method to generate the response
        response = assistant.print_response(message=message)
        return {"response": response}  # Return the response in the API response

    @app.get("/tools")
    async def get_tools():
        """
        Endpoint to get the list of tools available to the assistant.
        """
        return {"tools": assistant.tools}

    @app.post("/load_image")
    async def load_image(image_url: str):
        """
        Endpoint to load an image from a URL.
        """
        try:
            image = assistant.load_image_from_url(image_url)
            return {"status": "success", "image": "Image loaded successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return app