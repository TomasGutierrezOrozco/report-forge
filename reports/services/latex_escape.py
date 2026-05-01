import re

def escape_latex(text):
    """
    Escapes characters that have special meaning in LaTeX.
    """
    if not text:
        return ""
    
    # Define mapping of special characters to their LaTeX escaped versions
    # Backslash must be handled first to avoid escaping the backslashes added in other replacements
    latex_special_chars = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    
    # We don't want to escape characters inside commands or outputs, 
    # but Jinja2 will call this filter on normal text fields (like explanation, recommendation, etc.)
    
    # Build regex pattern for all keys
    pattern = re.compile('|'.join(re.escape(key) for key in latex_special_chars.keys()))
    
    # Replace using the mapping
    return pattern.sub(lambda match: latex_special_chars[match.group(0)], str(text))
