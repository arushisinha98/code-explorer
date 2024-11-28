import ast
from typing import Dict, List, Set

class PythonFileAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.imports = set()
        self.classes = {}
        self.global_funcs = set()
        self.global_vars = {}
        
    def parse_file(self) -> None:
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
            self._analyze_tree(tree)
    
    def _analyze_tree(self, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            # Get imports
            if isinstance(node, ast.Import):
                for name in node.names:
                    self.imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports.add(f"{node.module}.{node.names[0].name}")
            
            # Get classes and their methods
            elif isinstance(node, ast.ClassDef):
                class_info = {
                    'attributes': [],
                    'methods': {}
                }
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Extract attributes from __init__ method
                        if item.name == '__init__':
                            for stmt in item.body:
                                if isinstance(stmt, ast.Assign):
                                    for target in stmt.targets:
                                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                                            if target.value.id == 'self':
                                                class_info['attributes'].append(target.attr)
                
                        
                        class_info['methods'][item.name] = {
                            'docstring': ast.get_docstring(item) or "No documentation available",
                            'args': [arg.arg for arg in item.args.args],
                            'decorators': [ast.unparse(d) for d in item.decorator_list]
                        }
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_info['attributes'][target.id] = ast.unparse(item.value)
                self.classes[node.name] = class_info

            # Get global functions
            
            
            # Get global variables
            
    
    def get_summary(self) -> Dict:
        return {
            'imports': sorted(list(self.imports)),
            'classes': self.classes,
            'global_functions': sorted(list(self.global_funcs)),
            'global_variables': self.global_vars
        }

analyzer = PythonFileAnalyzer('../ads-deluge-frome/flood_tool/tool.py')
analyzer.parse_file()