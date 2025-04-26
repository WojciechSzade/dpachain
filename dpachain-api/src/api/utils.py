from fastapi import HTTPException
from src.block.errors import *


def handle_error(e: Exception):
    if isinstance(e, BlockNotFoundError):
        raise HTTPException(
            status_code=404, detail=f"Requested element was not found: {str(e)}")
    raise HTTPException(
        status_code=500, detail=f"An error occured while trying to perform the operation: {str(e)}")
