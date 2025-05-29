import asyncio
import json
import logging

import websockets
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)
User = get_user_model()


class StockMarketProxyConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.microservice_ws = None
        self.microservice_url = getattr(
            settings, "MICROSERVICE_WS_URL", "ws://localhost:8001/ws/stocks/"
        )
        self.user = None
        self.is_authenticated = False

    async def connect(self):
        """Handle WebSocket connection with JWT authentication"""
        await self.authenticate_user()

        if not self.is_authenticated:
            await self.close(code=4401)
            return

        await self.accept()

        await self.connect_to_microservice()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.microservice_ws:
            await self.microservice_ws.close()
            logger.info(
                f"Disconnected from microservice for user {self.user.id if self.user else 'unknown'}"
            )

    async def receive(self, text_data):
        """Receive message from client and forward to microservice"""
        if not self.microservice_ws:
            await self.send(
                text_data=json.dumps({"error": "Microservice connection not available"})
            )
            return

        try:
            data = json.loads(text_data)

            data["user_id"] = self.user.id
            data["user_email"] = self.user.email

            await self.microservice_ws.send(json.dumps(data))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
            await self.send(
                text_data=json.dumps({"error": "Failed to forward message"})
            )

    async def authenticate_user(self):
        try:
            token = None
            query_string = self.scope.get("query_string", b"").decode()

            if "token=" in query_string:
                for param in query_string.split("&"):
                    if param.startswith("token="):
                        token = param.split("=", 1)[1]
                        break

            if not token:
                headers = dict(self.scope.get("headers", []))
                auth_header = headers.get(b"authorization", b"").decode()
                if auth_header.startswith("Bearer "):
                    token = auth_header[7:]

            if not token:
                logger.warning("No JWT token provided")
                return

            access_token = AccessToken(token)
            user_id = access_token["user_id"]

            self.user = await self.get_user(user_id)
            if self.user:
                self.is_authenticated = True
                logger.info(f"User {self.user.id} authenticated successfully")

        except (InvalidToken, TokenError, KeyError) as e:
            logger.warning(f"JWT authentication failed: {e}")
        except Exception as e:
            logger.error(f"Authentication error: {e}")

    @database_sync_to_async
    def get_user(self, user_id):
        """Get user from database asynchronously"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def connect_to_microservice(self):
        """Connect to the microservice WebSocket"""
        try:
            microservice_url = f"{self.microservice_url}?user_id={self.user.id}"

            self.microservice_ws = await websockets.connect(
                microservice_url,
                extra_headers={
                    "X-User-ID": str(self.user.id),
                    "X-User-Email": self.user.email,
                },
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10,
            )

            asyncio.create_task(self.listen_to_microservice())

            logger.info(f"Connected to microservice WebSocket for user {self.user.id}")

        except Exception as e:
            logger.error(f"Failed to connect to microservice WebSocket: {e}")
            await self.send(
                text_data=json.dumps(
                    {"error": "Failed to connect to stock market service"}
                )
            )
            await self.close()

    async def listen_to_microservice(self):
        """Listen for messages from microservice and forward to client"""
        try:
            async for message in self.microservice_ws:
                await self.send(text_data=message)

        except websockets.exceptions.ConnectionClosed:
            logger.info("Microservice WebSocket connection closed")
            await self.send(
                text_data=json.dumps({"error": "Stock market service disconnected"})
            )
            await self.close()
        except Exception as e:
            logger.error(f"Error listening to microservice WebSocket: {e}")
            await self.send(
                text_data=json.dumps(
                    {"error": "Connection error with stock market service"}
                )
            )
            await self.close()


class HighPerformanceStockProxyConsumer(AsyncWebsocketConsumer):

    _connection_pool = {}
    _pool_lock = None

    @classmethod
    async def get_pool_lock(cls):
        """Get or create the pool lock"""
        if cls._pool_lock is None:
            cls._pool_lock = asyncio.Lock()
        return cls._pool_lock

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.microservice_ws = None
        self.microservice_url = getattr(
            settings, "MICROSERVICE_WS_URL", "ws://localhost:8001/ws/stocks/"
        )
        self.user = None
        self.is_authenticated = False

    async def connect(self):
        """Handle connection with authentication and pooled microservice connection"""
        await self.authenticate_user()

        if not self.is_authenticated:
            await self.close(code=4401)
            return

        await self.accept()

        await self.get_pooled_connection()

    async def disconnect(self, close_code):
        """Handle disconnection - don't close pooled connections immediately"""
        logger.info(
            f"Client disconnected for user {self.user.id if self.user else 'unknown'}"
        )

    async def receive(self, text_data):
        """Forward received messages to microservice"""
        if not self.microservice_ws:
            await self.send(
                text_data=json.dumps({"error": "Microservice connection not available"})
            )
            return

        try:
            data = json.loads(text_data)
            data["user_id"] = self.user.id
            data["user_email"] = self.user.email

            await self.microservice_ws.send(json.dumps(data))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
            await self.send(
                text_data=json.dumps({"error": "Failed to forward message"})
            )

    async def authenticate_user(self):
        """Same authentication logic as StockMarketProxyConsumer"""
        try:
            token = None
            query_string = self.scope.get("query_string", b"").decode()

            if "token=" in query_string:
                for param in query_string.split("&"):
                    if param.startswith("token="):
                        token = param.split("=", 1)[1]
                        break

            if not token:
                headers = dict(self.scope.get("headers", []))
                auth_header = headers.get(b"authorization", b"").decode()
                if auth_header.startswith("Bearer "):
                    token = auth_header[7:]

            if not token:
                logger.warning("No JWT token provided for WebSocket connection")
                return

            access_token = AccessToken(token)
            user_id = access_token["user_id"]

            self.user = await self.get_user(user_id)
            if self.user:
                self.is_authenticated = True
                logger.info(
                    f"User {self.user.id} authenticated successfully for WebSocket"
                )

        except (InvalidToken, TokenError, KeyError) as e:
            logger.warning(f"JWT authentication failed for WebSocket: {e}")
        except Exception as e:
            logger.error(f"Authentication error for WebSocket: {e}")

    @database_sync_to_async
    def get_user(self, user_id):
        """Get user from database asynchronously"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def get_pooled_connection(self):
        """Get a connection from the pool or create a new one"""
        pool_lock = await self.get_pool_lock()
        async with pool_lock:
            pool_key = f"user_{self.user.id}"

            if pool_key in self._connection_pool:
                self.microservice_ws = self._connection_pool[pool_key]
                if self.microservice_ws.closed:
                    del self._connection_pool[pool_key]
                    await self.create_new_connection(pool_key)
            else:
                await self.create_new_connection(pool_key)

    async def create_new_connection(self, pool_key):
        """Create a new connection and add to pool"""
        try:
            microservice_url = f"{self.microservice_url}?user_id={self.user.id}"

            self.microservice_ws = await websockets.connect(
                microservice_url,
                extra_headers={"X-User-ID": str(self.user.id)},
                ping_interval=30,
                ping_timeout=15,
            )

            self._connection_pool[pool_key] = self.microservice_ws
            asyncio.create_task(self.listen_to_microservice())

        except Exception as e:
            logger.error(f"Failed to create microservice connection: {e}")
            await self.close()

    async def listen_to_microservice(self):
        """Listen for messages from microservice and forward to client"""
        try:
            async for message in self.microservice_ws:
                await self.send(text_data=message)

        except websockets.exceptions.ConnectionClosed:
            logger.info("Microservice connection closed")
            await self.send(
                text_data=json.dumps({"error": "Stock market service disconnected"})
            )
            await self.close()
        except Exception as e:
            logger.error(f"Error listening to microservice: {e}")
            await self.send(
                text_data=json.dumps(
                    {"error": "Connection error with stock market service"}
                )
            )
            await self.close()
