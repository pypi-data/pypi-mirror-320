from typing import Dict, List, Union

from abc import ABC, abstractmethod
from endpoints.utils import append_string_or_list_of_string
from endpoints.schema import Schema, SchemaCollection

DEFAULT_INPUT_KEYS = ["text", "input_text", "texts", "input_texts"]


class BaseInferenceModel(ABC):
    def __init__(self, input: Schema, input_params: SchemaCollection, output: Schema):
        self._input = input
        assert (
            input._field in DEFAULT_INPUT_KEYS
        ), f"Input schema must contain one of the following keys: {DEFAULT_INPUT_KEYS}"

        self._input_params = input_params
        self._output = output

    def _validate_input(self, input_data: Union[Dict, List[Dict]]) -> Dict:
        inputs = []
        params = []

        def _validate_common_input(input: Dict):
            validated_input = self._input.validate(input)
            validated_input_params = self._input_params.validate(input)

            append_string_or_list_of_string(validated_input, inputs)

            # Append the same params for each input
            for input in inputs:
                params.append(validated_input_params)

        if isinstance(input_data, dict):
            _validate_common_input(input_data)

        if isinstance(input_data, list):
            for item in input_data:
                _validate_common_input(item)
            if not inputs:
                raise ValueError(
                    f"Input data must contain one of the following keys: {DEFAULT_INPUT_KEYS}"
                )

        return {"inputs": inputs, "params": params}

    def predict(self, input_data: Union[Dict, List[Dict]]) -> Dict:
        validated_data = self._validate_input(input_data)
        predictions = self.concrete_predict(validated_data)
        return {self._output._field: self._output.validate(predictions)}

    @abstractmethod
    def concrete_predict(self, input_data: Dict) -> Dict:
        pass

    @abstractmethod
    def get_python_requirements(self) -> List[str]:
        pass
