from __future__ import annotations

import functools
from typing import Sequence

import numpy as np
import pyarrow as pa

from chalk.features._embedding.embedding_provider import EmbeddingProvider
from chalk.features._vector import Vector
from chalk.utils.missing_dependency import missing_dependency_exception

try:
    import openai
    import tiktoken
except ImportError:
    openai = None
    tiktoken = None


MAX_INPUT_TOKENS = 8191


class OpenAIProvider(EmbeddingProvider):
    def __init__(self, model: str) -> None:
        super().__init__()
        if not openai or not tiktoken:
            raise missing_dependency_exception("chalkpy[openai]")
        if model not in {"text-embedding-ada-002", "text-embedding-3-small"}:
            raise ValueError(
                f"Unsupported model '{model}' for OpenAI. The supported models are ['text-embedding-ada-002', 'text-embedding-3-small']."
            )
        self.model = model

    @functools.cached_property
    def _async_client(self):
        assert openai
        return openai.AsyncOpenAI()

    @functools.cached_property
    def _encoding(self):
        assert tiktoken is not None, "Verified tiktoken is available in init"
        try:
            return tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Use cl100k_base encoding by default
            return tiktoken.get_encoding("cl100k_base")

    def get_provider_name(self) -> str:
        return "openai"

    def get_model_name(self) -> str:
        return self.model

    def validate_input_schema(self, input_schema: Sequence[pa.DataType]) -> str | None:
        if len(input_schema) != 1:
            return f"OpenAI emeddings support only 1 input, but got {len(input_schema)} inputs"
        if input_schema[0] != pa.large_utf8():
            return f"OpenAI embeddings require a large_utf8() feature, but got a feature of type {input_schema[0]}"

    def _truncate_embedding_input(self, input: str) -> str:
        if not isinstance(input, str):
            raise ValueError(f"Expected input to be a string, but got {type(input).__name__}: {input}")
        input_tokens = self._encoding.encode(input)
        if len(input_tokens) > MAX_INPUT_TOKENS:
            return self._encoding.decode(input_tokens[:MAX_INPUT_TOKENS])
        return input

    async def async_generate_embedding(self, input: pa.Table):
        assert openai
        inputs: list[str] = [self._truncate_embedding_input(i) for i in input.column(0).to_pylist()]
        # Step over `input` in chunks of 2048; the max openai array length
        for i in range(0, len(inputs), 2048):
            response = await self._async_client.embeddings.create(input=inputs[i : i + 2048], model=self.model)
            vectors = np.array(
                [entry.embedding for entry in response.data],
                dtype=np.dtype(self.get_vector_class().precision.replace("fp", "float")),
            )
            yield pa.FixedSizeListArray.from_arrays(vectors.reshape(-1), self.get_vector_class().num_dimensions)

    def generate_embedding(self, input: pa.Table) -> pa.FixedSizeListArray:
        assert openai
        inputs: list[str] = [self._truncate_embedding_input(i) for i in input.column(0).to_pylist()]
        response = openai.embeddings.create(input=inputs, model=self.model)
        vectors = np.array(
            [entry.embedding for entry in response.data],
            dtype=np.dtype(self.get_vector_class().precision.replace("fp", "float")),
        )
        return pa.FixedSizeListArray.from_arrays(vectors.reshape(-1), self.get_vector_class().num_dimensions)

    def get_vector_class(self) -> type[Vector]:
        return Vector[1536]
