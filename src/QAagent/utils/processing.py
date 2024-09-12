def process_block(text_block):
    if f"```python" in text_block:
        text_block = text_block[text_block.find(f"```python") + len(f"```python"):]
        text_block = text_block[:text_block.find("```")]
    elif f"```" in text_block:
        text_block = text_block[text_block.find(f"```") + len(f"```"):]
        text_block = text_block[:text_block.find("```")]
    else:
        print("Error: No text block found")
    return text_block