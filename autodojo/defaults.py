from ninja import Schema


class DefaultErrorResponseSchema(Schema):
    api_error: str
