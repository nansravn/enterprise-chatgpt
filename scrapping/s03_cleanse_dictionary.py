

# def normalize_line(line, prefix):
#     if line.strip().lower().startswith(prefix.lower()):
#         return ''
#     else:
#         return line

# def normalize_line_multiple_prefixes(line, prefixes):
#     for prefix in prefixes:
#         if line.strip().lower().startswith(prefix.lower()):
#             return ''
#     return line

# # Replace lines with only spaces with empty lines
#     text = '\n'.join([normalize_line_multiple_prefixes(line, ["Access the page", "Go Back"]) if line.strip() else '' for line in text.split('\n')])