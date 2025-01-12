import base64


def encode_token(token: str) -> str:
    return base64.b64encode(token.encode()).decode()


def decode_token(encoded_token: str) -> str:
    return base64.b64decode(encoded_token.encode()).decode()
