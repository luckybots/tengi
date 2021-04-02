

class CommandCard:
    def __init__(self, command_str: str, description: str, is_admin: bool):
        self.command_str = command_str
        self.description = description
        self.is_admin = is_admin
