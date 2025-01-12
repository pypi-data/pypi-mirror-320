from typing import Dict, List, Type


MODEL_LOCATION = "/opt/ml/model"
DEFAULT_INPUT_KEYS = ["text", "input_text", "texts", "input_texts"]


class SchemaValidationError(Exception):
    pass


class Schema:
    def __init__(
        self,
        field: str,
        typing: Type,
        default=None,
        required: bool = False,
        dtypes: List[str] = [],
    ):
        self._field = field
        self._required = required
        self._typing = typing
        self._dtypes = dtypes
        self._default = default

    def validate(self, data: Dict):
        if self._required and self._field not in data:
            raise SchemaValidationError(f"Key {self._field} is missing in the data")
        value = data.get(self._field, self._default)
        if self._dtypes:
            if value not in self._dtypes:
                raise SchemaValidationError(
                    f"Key {self._field} must be of type {self._dtypes}"
                )
        if isinstance(value, list):
            for item in value:
                if not isinstance(item, self._typing):
                    raise SchemaValidationError(
                        f"Key {self._field} must be of type {self._typing}"
                    )
        elif not isinstance(value, self._typing):
            raise SchemaValidationError(f"Key {value} must be of type {self._typing}")
        return value


class SchemaCollection:
    def __init__(self, schemas: List[Schema]):
        self._schemas = schemas

    def validate(self, data: Dict):
        return {schema._field: schema.validate(data) for schema in self._schemas}
