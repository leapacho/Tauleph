def extract_think(response_text: str) -> str:
    """Split the response on the </think> tag and take the text after it"""
    if "</think>" in response_text:
        parts = response_text.split("</think>")
        if len(parts) > 1:
            no_think_tags=parts[0].replace("<think>", "")
            return parts[1].strip(), no_think_tags
        return response_text.strip()
    else:
        nothing=""
        no_think_tags=response_text.replace("<think>", "")
        return no_think_tags.strip(), nothing