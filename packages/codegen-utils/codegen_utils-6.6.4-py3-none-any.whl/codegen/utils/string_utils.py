def truncate_line(input: str, max_chars: int) -> str:
    input = str(input)
    if len(input) > max_chars:
        return input[:max_chars] + f"...(truncated from {len(input)} characters)."
    return input
