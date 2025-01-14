"""API Gateway event resolvers for Lambda functions.

Provides REST and HTTP API Gateway event handling with routing capabilities.
"""

from typing import Any, Callable, Optional, TypeVar, Union, Generic
from enum import Enum
import re

from pydantic import BaseModel

from chainsaws.aws.lambda_client.event_handler.handler_models import LambdaResponse, LambdaEvent
from chainsaws.aws.lambda_client.types.events.api_gateway_proxy import (
    APIGatewayProxyV1Event,
    APIGatewayProxyV2Event,
)
from chainsaws.aws.lambda_client.event_handler.middleware import MiddlewareManager, Middleware

T = TypeVar("T", APIGatewayProxyV1Event, APIGatewayProxyV2Event)
RouteHandler = TypeVar("RouteHandler", bound=Callable[..., Any])


class HttpMethod(str, Enum):
    """HTTP methods supported by API Gateway."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class Route(BaseModel):
    """API Gateway route definition."""
    path: str
    method: HttpMethod
    handler: Callable[..., Any]
    cors: bool = True


class BaseResolver(Generic[T]):
    """Base resolver for API Gateway events."""

    def __init__(self):
        self.routes: list[Route] = []
        self.middleware_manager: MiddlewareManager[T] = MiddlewareManager()

    def add_middleware(self, middleware: Middleware) -> None:
        """Add a middleware to the resolver."""
        self.middleware_manager.add_middleware(middleware)

    def middleware(self, middleware_func: Middleware) -> Middleware:
        """Decorator to add a middleware."""
        self.add_middleware(middleware_func)
        return middleware_func

    def add_route(
        self,
        path: str,
        method: Union[str, HttpMethod],
        cors: bool = True
    ) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator to add a route handler."""
        if isinstance(method, str):
            method = HttpMethod(method.upper())

        def decorator(handler: RouteHandler) -> RouteHandler:
            route = Route(
                path=path,
                method=method,
                handler=handler,
                cors=cors
            )
            self.routes.append(route)
            return handler
        return decorator

    def get(self, path: str, cors: bool = True) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for GET method routes."""
        return self.add_route(path, HttpMethod.GET, cors)

    def post(self, path: str, cors: bool = True) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for POST method routes."""
        return self.add_route(path, HttpMethod.POST, cors)

    def put(self, path: str, cors: bool = True) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for PUT method routes."""
        return self.add_route(path, HttpMethod.PUT, cors)

    def delete(self, path: str, cors: bool = True) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for DELETE method routes."""
        return self.add_route(path, HttpMethod.DELETE, cors)

    def patch(self, path: str, cors: bool = True) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for PATCH method routes."""
        return self.add_route(path, HttpMethod.PATCH, cors)

    def head(self, path: str, cors: bool = True) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for HEAD method routes."""
        return self.add_route(path, HttpMethod.HEAD, cors)

    def options(self, path: str, cors: bool = True) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for OPTIONS method routes."""
        return self.add_route(path, HttpMethod.OPTIONS, cors)

    def _find_route(self, path: str, method: str) -> Optional[Route]:
        """Find matching route for path and method."""
        for route in self.routes:
            if route.method.value == method.upper():
                # Convert route pattern to regex
                pattern = re.sub(r'{([^:}]+)(?::([^}]+))?}',
                                 r'(?P<\1>[^/]+)', route.path)
                match = re.match(f'^{pattern}$', path)
                if match:
                    return route
        return None

    def resolve(self, event: T, context: Any = None) -> dict[str, Any]:
        """Resolve API Gateway event to handler response."""
        raise NotImplementedError


class APIGatewayRestResolver(BaseResolver[APIGatewayProxyV1Event]):
    """Resolver for REST API Gateway events."""

    def resolve(self, event: APIGatewayProxyV1Event, context: Any = None) -> dict[str, Any]:
        """Resolve REST API Gateway event to handler response."""
        # Validate event structure
        if event.get('version', '1.0') != '1.0':
            return LambdaResponse.create(
                {"message":
                    "Invalid API Gateway version. Expected REST API (v1)"},
                status_code=400
            )

        lambda_event = LambdaEvent.model_validate(event)

        path = event.get('path', '')
        method = event.get('httpMethod', '')

        route = self._find_route(path, method)
        if not route:
            return LambdaResponse.create(
                {"message": "Not Found"},
                status_code=404
            )

        try:
            # Extract path parameters
            pattern = re.sub(r'{([^:}]+)(?::([^}]+))?}',
                             r'(?P<\1>[^/]+)', route.path)
            match = re.match(f'^{pattern}$', path)
            path_params = match.groupdict() if match else {}

            # Prepare kwargs for handler
            kwargs = {
                "event": lambda_event,
                "context": context,
                "path_parameters": path_params,
                "query_parameters": event.get('queryStringParameters', {}),
                "headers": event.get('headers', {}),
                "body": lambda_event.get_json_body()
            }

            # Apply middleware chain to the handler
            handler = self.middleware_manager.apply(
                lambda e, c: route.handler(
                    **{**kwargs, "event": e, "context": c})
            )
            result = handler(event, context)

            # If result is already a dict with statusCode, assume it's properly formatted
            if isinstance(result, dict) and "statusCode" in result:
                return result

            return LambdaResponse.create(result)

        except Exception as e:
            return LambdaResponse.create(
                {"message": str(e)},
                status_code=500
            )


class APIGatewayHttpResolver(BaseResolver[APIGatewayProxyV2Event]):
    """Resolver for HTTP API Gateway events."""

    def resolve(self, event: APIGatewayProxyV2Event, context: Any = None) -> dict[str, Any]:
        """Resolve HTTP API Gateway event to handler response."""
        # Validate event structure
        if event.get('version', '2.0') != '2.0':
            return LambdaResponse.create(
                {"message":
                    "Invalid API Gateway version. Expected HTTP API (v2)"},
                status_code=400
            )

        lambda_event = LambdaEvent.model_validate(event)

        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get(
            'http', {}).get('method', '')

        route = self._find_route(path, method)
        if not route:
            return LambdaResponse.create(
                {"message": "Not Found"},
                status_code=404
            )

        try:
            # Extract path parameters
            pattern = re.sub(r'{([^:}]+)(?::([^}]+))?}',
                             r'(?P<\1>[^/]+)', route.path)
            match = re.match(f'^{pattern}$', path)
            path_params = match.groupdict() if match else {}

            # Prepare kwargs for handler
            kwargs = {
                "event": lambda_event,
                "context": context,
                "path_parameters": path_params,
                "query_parameters": event.get('queryStringParameters', {}),
                "headers": event.get('headers', {}),
                "body": lambda_event.get_json_body()
            }

            # Apply middleware chain to the handler
            handler = self.middleware_manager.apply(
                lambda e, c: route.handler(
                    **{**kwargs, "event": e, "context": c})
            )
            result = handler(event, context)

            # If result is already a dict with statusCode, assume it's properly formatted
            if isinstance(result, dict) and "statusCode" in result:
                return result

            return LambdaResponse.create(result)

        except Exception as e:
            return LambdaResponse.create(
                {"message": str(e)},
                status_code=500
            )
