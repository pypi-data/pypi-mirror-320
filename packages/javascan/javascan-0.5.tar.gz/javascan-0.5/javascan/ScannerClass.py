import re

# Version 3

class JavaCodeLinter:
    def __init__(self):
        self.errors = []

    def lint(self, code: str):
        self.errors = []
        self.check_class_declaration(code)
        self.check_method_naming(code)
        self.check_variable_naming(code)
        return self.errors

    def check_class_declaration(self, code):
        """Check for proper class declaration."""
        class_pattern = re.compile(r"^\s*class\s+[A-Z][a-zA-Z0-9]*\s*{")
        for i, line in enumerate(code.splitlines(), 1):
            if "class" in line and not class_pattern.match(line):
                self.errors.append(f"Line {i}: Invalid class declaration. Class names should start with an uppercase letter and contain only letters/numbers.")

    def check_method_naming(self, code):
        """Check that methods follow camelCase naming convention."""
        method_pattern = re.compile(r"^\s*(public|private|protected)?\s+[a-zA-Z0-9<>]+\s+[a-z][a-zA-Z0-9]*\s*\(")
        for i, line in enumerate(code.splitlines(), 1):
            if "(" in line and not method_pattern.match(line):
                self.errors.append(f"Line {i}: Invalid method naming. Methods should follow camelCase naming convention.")

    def check_variable_naming(self, code):
        """Check that variables follow camelCase naming convention."""
        variable_pattern = re.compile(r"^\s*[a-z][a-zA-Z0-9]*\s*=")
        for i, line in enumerate(code.splitlines(), 1):
            if "=" in line and not variable_pattern.match(line):
                self.errors.append(f"Line {i}: Invalid variable naming. Variables should follow camelCase naming convention.")
