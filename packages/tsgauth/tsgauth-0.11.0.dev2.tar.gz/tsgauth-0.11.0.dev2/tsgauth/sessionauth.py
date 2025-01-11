import tsgauth 
from fastapi import Request, HTTPException
from aiocache import Cache
from typing import Optional, Dict, Any
import uuid
import requests
import time

class SessionAuthTokenStore(tsgauth.fastapi.SessionAuthBase):
    if tsgauth.fastapi.settings.oidc_session_store_type == "memory":
        cache = Cache(Cache.MEMORY)        
    else:
        cache = Cache(Cache.REDIS,endpoint=f"{tsgauth.fastapi.settings.oidc_session_store_host}:{tsgauth.fastapi.settings.oidc_session_store_port}")
    class SessionAuthData:
        def __init__(self, session_id : Optional[str] = None, auth_try_count : int = 0, **kwargs):
            self.session_id = session_id
            self.auth_try_count = auth_try_count
        def to_dict(self) -> Dict[str, Any]:
            return {"session_id": self.session_id, "auth_try_count": self.auth_try_count}
        def from_dict(self, data : Dict[str, Any]):
            self.session_id = data.get("session_id",None)
            self.auth_try_count = data.get("auth_try_count",0)
        
    @classmethod
    async def claims(cls,request: Request) -> Dict[str, Any]:
        auth_session_data = cls._get_auth_data(request)
        
        if auth_session_data.session_id is None:
            auth_session_data.session_id = str(uuid.uuid4())
            cls._set_auth_data(request, auth_session_data)
        if await cls.cache.exists(auth_session_data.session_id):
            token_data = await cls.cache.get(auth_session_data.session_id)
            
            if time.time() > token_data.get("access_exp",0):
                await cls._renew_token(request)
            token_data = await cls.cache.get(auth_session_data.session_id)
            key = token_data.get("key",None)
            return tsgauth.fastapi._parse_token_fastapi(token_data["access_token"],key = key)
            
        raise tsgauth.fastapi.MissingAuthException(status_code=401, detail="No authentication credentials provided.")
    
    @classmethod
    async def store(cls,request: Request, auth_response : Dict[str, Any]) -> None:
        try:
            access_token = auth_response["access_token"]
        except KeyError:
            raise cls.AuthResponseException("No access token in response")
        
        refresh_token = auth_response.get("refresh_token")

        try:
            #TODO: hmm key set over just key?
            key = requests.get(tsgauth.fastapi.settings.oidc_jwks_uri).json()["keys"][0]
        except Exception as e:
            raise cls.AuthResponseException("Could not get key from jwks_uri")
        
        try:
            #really just to check the token is valid
            _parse_token_fastapi(access_token,key = key)
        except Exception as e:
            raise cls.AuthResponseException("Invalid or expired token in response") 
        
        auth_session_data = cls._get_auth_data(request)
        await cls.cache.set(auth_session_data.session_id, {"access_token" : access_token,
                                                           "refresh_token" : refresh_token,
                                                           "key" : key,
                                                           }, ttl=tsgauth.fastapi.settings.oidc_session_claims_lifetime)
        
        auth_session_data.auth_try_count = 0
        cls._set_auth_data(request, auth_session_data)

    @classmethod
    async def token_request_allowed(cls,request: Request) -> bool:
        return  tsgauth.fastapi.settings.oidc_allow_token_request and cls._get_auth_data(request).auth_try_count < 3
    
    @classmethod
    async def auth_attempt(cls,request: Request) -> None:
        auth_data = cls._get_auth_data(request)
        auth_data.auth_try_count += 1        
        cls._set_auth_data(request, auth_data)
        if not await cls.token_request_allowed(request):
            await cls.clear(request)
            raise HTTPException(status_code=401, detail="Too many token reqeusts")

    @classmethod
    async def clear(cls,request: Request) -> None:        
        auth_data = cls._get_auth_data(request)
        if auth_data.session_id:
            await cls.cache.delete(auth_data.session_id)
        cls._del_auth_data(request)
        
    
    @classmethod
    def _get_auth_data(cls,request:Request) -> SessionAuthData:
        if not hasattr(request, "session"):
            raise HTTPException(status_code=500, detail="Session middleware not configured correctly")
        return cls.SessionAuthData(**request.session.get("auth_data", {}))
    
    @classmethod
    def _set_auth_data(cls,request:Request, auth_data : SessionAuthData) -> None:
        if not hasattr(request, "session"):
            raise HTTPException(status_code=500, detail="Session middleware not configured correctly")
        request.session["auth_data"] = auth_data.to_dict()

    @classmethod
    def _del_auth_data(cls,request:Request) -> None:
        if not hasattr(request, "session"):
            raise HTTPException(status_code=500, detail="Session middleware not configured correctly")
        if "auth_data" in request.session:
            del request.session["auth_data"]    

    @classmethod
    async def _renew_token(cls,request:Request) -> None:
        auth_session_data = cls._get_auth_data(request)
        token_data = await cls.cache.get(auth_session_data.session_id)

        refresh_token = token_data.get("refresh_token",None)
        if refresh_token is None:
            raise tsgauth.fastapi.MissingAuthException(status_code=401, detail="Token refresh required but no refresh token available")
        
        try:
            token_response = requests.post(tsgauth.fastapi.settings.oidc_token_uri, data={"grant_type" : "refresh_token",
                                                                         "refresh_token" : refresh_token,
                                                                         "client_id" : tsgauth.fastapi.settings.oidc_client_id})
            token_response.raise_for_status()
            token_data = token_response.json()
            await cls.store(request,token_data)
        except Exception as e:
            raise cls.AuthResponseException("Token renewal failed")
        
        return token_data