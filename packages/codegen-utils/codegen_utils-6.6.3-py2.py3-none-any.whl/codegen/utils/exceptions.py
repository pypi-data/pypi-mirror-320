class NotEnoughTokensException(Exception):
    """Raised when there aren't enough tokens to run a query with a given model."""

    def __init__(self, model, query_num_tokens, model_max_tokens) -> None:
        self.message = f"Not enough tokens to run model: {model} query_num_tokens: {query_num_tokens} vs model_max_tokens: {model_max_tokens}"
        super().__init__(self.message)
