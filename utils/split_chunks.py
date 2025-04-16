from textwrap import TextWrapper

def split_text(text: str, chunk_size: int) -> list:
    """
        Converts the input text into a list to then split it in chunks of the specified size in characters.\n
        
        Parameters:
            text (str): String to be processed.
            chunk_size (int): The size of the chunk. This is measured in characters. e.g. a chunk size of 100 will split a string of a 1000 characters every 100 characters.
        Returns:
            list: A list with the string split into chunks.
        Example:
            >>> test = "Hi, this sentence is 35 characters. This one is also 35 characters, hi. This tiny one is isn't. This sentence is more than 35 characters, isn't it cool?"\n
            >>> split_text_into_chunks(test, 35)
            ['Hi, this sentence is 35 characters.', 'This one is also 35 characters, hi.', "This tiny one isn't. This sentence", "is more than 35 characters, isn't", 'it cool?']
    """

    w = TextWrapper(width=chunk_size,break_long_words=True,replace_whitespace=False)
    chunked_lines=w.wrap(text)
    return chunked_lines