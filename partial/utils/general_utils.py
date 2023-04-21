import uuid


def generate_uuid4() -> str:
    """Generate a random UUID4.

    Returns:
        (str): Random UUID4
    """
    return str(uuid.uuid4())
