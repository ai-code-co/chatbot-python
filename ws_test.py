import asyncio
import websockets
import json

async def test_ws():
    # Replace user_id 123 with any external_id you want to test
    uri = "ws://127.0.0.1:8000/ws/chat/123/"

    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket!")

        # Send a test message
        message = {"message": "Hello from console test!"}
        await websocket.send(json.dumps(message))
        print("Sent:", message)

        # Wait for a response
        response = await websocket.recv()
        print("Received:", response)

        # Optionally, send another message
        message2 = {"message": "How are you?"}
        await websocket.send(json.dumps(message2))
        print("Sent:", message2)

        response2 = await websocket.recv()
        print("Received:", response2)

asyncio.run(test_ws())
