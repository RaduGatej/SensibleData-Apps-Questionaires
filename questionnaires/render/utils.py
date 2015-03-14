import re

def htmlize(string):
	return re.sub('[^a-z_0-9-:]','',string.strip().lower().replace(' ','_'));

def escape(t):
    """HTML-escape the text in `t`."""
    return (t
        .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace("'", "&#39;").replace('"', "&quot;")
        )
