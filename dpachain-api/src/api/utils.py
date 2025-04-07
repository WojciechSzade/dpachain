def handle_error(e: Exception):
    return {"message": f"An error occured while trying to perform the operation: {str(e)}"}