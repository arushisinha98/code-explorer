import ast
from typing import Dict
import tkinter as tk
from tkinter import ttk

class ClassVisualizer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.root = tk.Tk()
        self.root.title("Class Visualizer")
        
    def parse_class(self) -> Dict:
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
            
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Tool":
                return self._extract_class_info(node)
        return {}
    
    def _extract_class_info(self, node: ast.ClassDef) -> Dict:
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
                
                docstring = ast.get_docstring(item)
                class_info['methods'][item.name] = {
                    'docstring': docstring or "No documentation available"
                }
                
        return class_info
        
    def create_visualization(self):
        class_info = self.parse_class()
        
        # Create tree view
        tree = ttk.Treeview(self.root)
        tree.pack(expand=True, fill='both')
        
        # Add class attributes
        attr_node = tree.insert("", "end", text="Attributes", open=True)
        for attr in class_info['attributes']:
            tree.insert(attr_node, "end", text=attr)
            
        # Add methods
        method_node = tree.insert("", "end", text="Methods", open=True)

        # In create_visualization method, update the method insertion:
        for method, info in class_info['methods'].items():
            docstring = info['docstring'] if info['docstring'] else "No documentation available"
            tree.insert(method_node, "end", text=method, 
                    values=(docstring,))
        
        # Add tooltip functionality
        self._create_tooltip(tree)
        
        self.root.mainloop()
        
    def _create_tooltip(self, tree):
    # Create a new toplevel window for displaying docstrings
        def show_docstring(event):
            item = tree.selection()[0]  # Get selected item
            values = tree.item(item)['values']
            method_name = tree.item(item)['text']
            
            # Create a new toplevel window
            doc_window = tk.Toplevel(self.root)
            doc_window.title(f"Documentation: {method_name}")
            
            # Add text widget to display docstring
            text = tk.Text(doc_window, wrap=tk.WORD, width=60, height=10, 
                        padx=10, pady=10)
            text.pack(expand=True, fill='both')
            
            # Insert documentation text
            if values and len(values) > 0:
                text.insert('1.0', values[0])
            else:
                text.insert('1.0', f"No documentation available for {method_name}")
            
            # Make text widget read-only
            text.configure(state='disabled')
            
            # Center the window
            doc_window.geometry("500x300")
            doc_window.transient(self.root)
            doc_window.focus_set()
        
        # Bind double-click event
        tree.bind('<Double-1>', show_docstring)


visualizer = ClassVisualizer('../ads-deluge-frome/flood_tool/tool.py')
visualizer.create_visualization()
