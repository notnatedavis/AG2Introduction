#   agents/webpage_agent.py
#   Agent specialized in generating web pages (HTML/CSS)

# ----- Imports -----
from .base_agent import create_assistant_agent

# ----- Main -----
class WebpageAgent :
    # An agent that generates HTML/CSS web pages
    
    def __init__(self, name: str = "web_designer") :
        system_message = (
            "You are a creative web designer. You write clean HTML and CSS. "
            "When asked to create a webpage, you provide the full HTML code including inline CSS. "
            "You can use the write_html_file function to save your work. "
            "Reply 'TERMINATE' when done."
        )
        self.agent = create_assistant_agent(name, system_message)
    
    def get_agent(self) :
        return self.agent