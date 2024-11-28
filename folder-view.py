import os
import ast
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import numpy as np
import fnmatch

class DependencyVisualizer:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.graph = nx.DiGraph()
        self.folder_to_files = defaultdict(list)
        self.ignored_patterns = self._get_ignore_patterns()
        self.file_colors = {
            '.py': '#ADD8E6',    # Light blue for Python
            '.md': '#98FB98',    # Light green for markdown
            '.txt': '#98FB98',   # Light green for text
            '.yml': '#DDA0DD',   # Plum for yaml
            '.json': '#F0E68C',  # Khaki for json
            '.sh': '#FFB6C1'     # Light pink for no extension
        }

    def _get_file_color(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        return self.file_colors.get(ext, '#D3D3D3')  # Grey for unknown extensions
        
    def _get_ignore_patterns(self):
        gitignore_path = Path(self.folder_path) / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as file:
                # Filter out comments and empty lines
                return [line.strip() for line in file 
                       if line.strip() and not line.startswith('#')]
        return ['.*',
                '.pytest_cache/*',
                '*.pyc',
                '.git/',
                '.git/*',
                '.github/',
                '.github/*',
                '__pycache__',
                '__pycache__/*']
    
    def _should_ignore(self, path):
        rel_path = str(path).replace(self.folder_path, '').lstrip('/')
        
        # Explicitly check for .git and .github directories
        if '.git' in Path(rel_path).parts or '.github' in Path(rel_path).parts:
            return True
        
        # Skip files with no extension
        if os.path.isfile(path) and not os.path.splitext(path)[1]:
            return True
            
        for pattern in self.ignored_patterns:
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            if fnmatch.fnmatch(os.path.basename(rel_path), pattern):
                return True
        return False
        
    def build_file_structure(self):
        for root, dirs, files in os.walk(self.folder_path):
            # Filter directories first - modify dirs in place
            dirs[:] = [d for d in dirs if not self._should_ignore(os.path.join(root, d))]
            
            relative_path = os.path.relpath(root, self.folder_path)
            if relative_path == '.':
                relative_path = os.path.basename(self.folder_path)
            
            # Skip if the current directory should be ignored
            if self._should_ignore(root):
                continue
                
            # Filter and sort files
            valid_files = sorted([f for f in files 
                                if not self._should_ignore(os.path.join(root, f))])
            if valid_files:
                self.folder_to_files[relative_path] = valid_files
    
    def visualize(self):
        plt.figure(figsize=(12, 8))
        ax = plt.gca()
        ax.set_xlim(0, 2)
        y = 0
        
        for folder, files in sorted(self.folder_to_files.items()):
            if not files:  # Skip empty folders
                continue
                
            y -= 1
            # Draw folder name
            ax.text(0.1, y + 0.5, folder, fontsize=12, 
                   fontweight='bold', ha='left')
            
            # Calculate box height based on number of files
            box_height = len(files) * 0.5 + 1
            # Draw box around folder contents
            ax.add_patch(plt.Rectangle((0.05, y - box_height + 1), 1.9, 
                                     box_height, fill=False, 
                                     edgecolor='gray', lw=1))
            
            # Draw files
            for file in files:
                ax.text(0.2, y, file, fontsize=10, ha='left')
                # Add colored background for file
                ax.add_patch(plt.Rectangle((0.15, y - 0.2), 1.7, 0.4, 
                                         alpha=0.3,
                                         facecolor=self._get_file_color(file)))
                y -= 0.5
            
            y -= 0.5  # Add space between folders

        ax.set_ylim(y - 0.5, 1)
        ax.axis('off')
        plt.tight_layout()
        plt.show()


# Test implementation
visualizer = DependencyVisualizer('../ads-deluge-frome')
visualizer.build_file_structure()
visualizer.visualize()