from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.database.database import SessionLocal
from app.services.auth_service import validate_access_token
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request:Request, call_next):
        #define public routes that do not require authentication
        public_paths=[
            "/",
            "/login",
            "/register",
            "/auth/login",
            "/auth/register",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico"
        ]
        #Allow public routes and static files without authentication 
        if request.url.path in public_paths or request.url.path.startswith("/static"):
            return await call_next(request)
        #Extract and validate the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer") :
            return Response(
                content='{"details":"Authorization token required"}',
                status_code = 401,
                media_type ="application/json"
            )
        token = auth_header.split(" ",1)[1]
        #validate the access token and identify the user
        db= SessionLocal()
        try:
            user = validate_access_token(token,db)
            if not user:
                return Response(
                    content = '{"deatils":"Invalid or expired token"}',
                    status_code = 401,
                    media_type ="application/json"
                )
            request.state.user = user
            return await call_next(request)
        finally:
            db.close()