from typing import Optional

class Tools:
    def __init__(self):
        pass
    
    def generate_landing_page(self, niche: str, details: Optional[str] = "") -> str:
        """
        Generate a landing page using jonjon Agent
        """
        import subprocess
        import os
        
        # نفذ الـ agent
        result = subprocess.run(
            ["python3", "/Users/hichem/jonjon-lab/agents/html_agent_research.py"],
            input=f"{niche}\n{details}\n",
            text=True,
            capture_output=True,
            cwd="/Users/hichem/jonjon-lab"
        )
        
        return result.stdout
    
    def list_local_templates(self) -> str:
        """
        List available local templates
        """
        import os
        templates_dir = "/Users/hichem/jonjon-lab/templates"
        if not os.path.exists(templates_dir):
            return "No templates found"
        
        templates = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
        return "\n".join(templates) if templates else "No templates found"
