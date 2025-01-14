import base64
from typing import Protocol


class WorkspaceCodeToolbox(Protocol):
    def get_default_image(self) -> str: ...
    def get_run_command(self, code: str) -> str: ...


class WorkspaceTsCodeToolbox:
    def get_default_image(self) -> str:
        return "daytonaio/ai-test:0.1.0"  # todo: replace with ts image

    def get_run_command(self, code: str) -> str:
        base64_code = base64.b64encode(code.encode()).decode()
        return f"python3 -c \"exec(__import__('base64').b64decode('{base64_code}').decode())\""
