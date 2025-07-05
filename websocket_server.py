import asyncio
import websockets
import os
import logging

logging.basicConfig(level=logging.INFO)

PORT = int(os.environ.get("PORT", 8765))
connected_clients = set()


async def safe_send(client, message):
    try:
        await client.send(message)
    except websockets.exceptions.ConnectionClosed:
        connected_clients.discard(client)
    except Exception as e:
        logging.warning(f"Error sending to client: {e}")


async def handler(websocket):
    logging.info(f"New client connected: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            logging.info(
                f"Received message from {websocket.remote_address}: {message}")
            # Broadcast to all connected clients INCLUDING sender
            await asyncio.gather(
                *[safe_send(client, message) for client in connected_clients]
            )
    except websockets.exceptions.ConnectionClosed:
        logging.info(f"Client disconnected: {websocket.remote_address}")
    except Exception as e:
        logging.error(f"Handler error: {e}")
    finally:
        connected_clients.discard(websocket)
        logging.info(f"Client removed: {websocket.remote_address}")


async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        logging.info(f"WebSocket server started on port {PORT}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
