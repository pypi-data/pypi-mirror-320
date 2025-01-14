from fastapi import status, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Callable, Optional


def get_bearer_validator(
    tokens: Optional[list[str]] = None,
    get_tokens: Optional[Callable[[], list[str]]] = None,
):
    """
    Get a simple Bearer Token validator dependency.
    Use in routes with dependencies=[Depends(get_bearer_validator(tokens))].
    
    Args:
        tokens (list[str]): List of allowed tokens.
        get_tokens (Callable[[], list[str]]): Function to retrieve allowed tokens.
    
    Returns:
        Callable[..., None]: Dependency
    """
    assert tokens or get_tokens, 'tokens or get_tokens must be provided'
    
    def bearer_validator(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        token = credentials.credentials
        if tokens is not None:
            valid_tokens = tokens
        else:
            valid_tokens = get_tokens()
            
        if token not in valid_tokens:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Invalid or expired token")
        
    return bearer_validator
