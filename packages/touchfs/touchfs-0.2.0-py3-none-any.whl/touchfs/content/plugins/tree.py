"""Tree generator that creates a structured, greppable filesystem tree visualization."""
import os
from typing import Any, Dict, List, Optional, Tuple
from ...models.filesystem import FileNode, FileAttrs
from .proc import ProcPlugin
from ...config.settings import find_nearest_prompt_file, find_nearest_model_file

def get_prompt_excerpt(content: str, width: int) -> str:
    """Get a single-line excerpt from a prompt file's content.
    
    Args:
        content: The full prompt content
        width: Available width for the excerpt
        
    Returns:
        A single-line excerpt, truncated if needed
    """
    # Remove newlines and extra spaces
    content = ' '.join(content.split())
    if width < 3:  # Not enough space even for "..."
        return ""
    if len(content) > width:
        return content[:width-3] + "..."
    return content

class TreeGenerator(ProcPlugin):
    """Generator that creates a structured tree visualization in .touchfs directory."""
    
    def generator_name(self) -> str:
        return "tree"
    
    def get_proc_path(self) -> str:
        return "tree"
    
    def _convert_to_filenode(self, node: Dict[str, Any]) -> FileNode:
        """Convert a dictionary node to a FileNode object."""
        if isinstance(node, FileNode):
            return node
            
        # Ensure we have valid attrs
        attrs = node.get("attrs", {})
        if not attrs:
            attrs = {"st_mode": "33188"}  # Default to regular file with 644 permissions
            
        # Create FileNode with all optional fields
        return FileNode(
            type=node.get("type", "file"),
            content=node.get("content", ""),
            children=node.get("children"),  # Keep children if present
            attrs=FileAttrs(**attrs),
            xattrs=node.get("xattrs", {})
        )

    def _calculate_dimensions(self, path: str, structure: Dict[str, Any], indent: str = "") -> Tuple[int, int]:
        """Calculate the maximum width needed for tree structure and generator info.
        
        Returns:
            Tuple of (tree_width, info_width)
        """
        tree_width = len(indent)
        info_width = 0
        
        # Get children either from node's children attribute or by finding paths that have this as parent
        current_node = structure[path]
        if hasattr(current_node, 'children') and current_node.children:
            children = current_node.children
            names = list(children.keys())
            child_paths = [children[name] for name in names]
        else:
            # Find all paths that have this path as their parent
            children = {}
            for p in structure:
                if p != path and os.path.dirname(p) == path:
                    name = os.path.basename(p)
                    children[name] = p
            names = list(children.keys())
            child_paths = [children[name] for name in names]
        
        for i, name in enumerate(names):
            child_path = child_paths[i]
            child_node = self._convert_to_filenode(structure[child_path])
            is_last = i == len(names) - 1
            
            prefix = "└── " if is_last else "├── "
            child_indent = indent + ("    " if is_last else "│   ")
            
            # Calculate width for this line
            line_width = len(indent) + len(prefix) + len(name)
            tree_width = max(tree_width, line_width)
            
            # Calculate generator info width
            if child_node.type == "file":
                if child_node.xattrs:
                    if "generator" in child_node.xattrs:
                        info_width = max(info_width, len(child_node.xattrs["generator"]) + 2)
                    elif child_node.xattrs.get("generate_content") == "true":
                        # Account for "default" + paths
                        info_width = max(info_width, 50)  # Reasonable default for path display
            
            # Recursively check children if this is a directory
            if child_node.type == "directory":
                child_tree_width, child_info_width = self._calculate_dimensions(child_path, structure, child_indent)
                tree_width = max(tree_width, child_tree_width)
                info_width = max(info_width, child_info_width)
        
        return tree_width, info_width

    def _build_tree(self, path: str, structure: Dict[str, Any], indent: str = "", dimensions: Tuple[int, int] = (0, 0)) -> List[str]:
        """Build a tree representation of the filesystem structure."""
        result = []
        tree_width, info_width = dimensions
        
        # Get children either from node's children attribute or by finding paths that have this as parent
        current_node = structure[path]
        if hasattr(current_node, 'children') and current_node.children:
            children = current_node.children
            names = list(children.keys())
            child_paths = [children[name] for name in names]
        else:
            # Find all paths that have this path as their parent
            children = {}
            for p in structure:
                if p != path and os.path.dirname(p) == path:
                    name = os.path.basename(p)
                    children[name] = p
            names = list(children.keys())
            child_paths = [children[name] for name in names]
        
        for i, name in enumerate(names):
            child_path = child_paths[i]
            child_node = self._convert_to_filenode(structure[child_path])
            is_last = i == len(names) - 1
            
            # Choose the appropriate symbols
            prefix = "└── " if is_last else "├── "
            child_indent = indent + ("    " if is_last else "│   ")
            
            # Build the base line with consistent width
            base_line = f"{indent}{prefix}{name}"
            
            # Add generator info in aligned column
            generator_info = ""
            if child_node.type == "file":
                # Handle special files first
                if name.endswith(('.prompt', '.touchfs.prompt')):
                    if child_node.content:
                        padding = " " * (tree_width - len(base_line))
                        excerpt = get_prompt_excerpt(child_node.content, 80)  # More reasonable width
                        generator_info = f"{padding} │ 📝 {excerpt}"
                elif name.endswith(('.model', '.touchfs.model')):
                    if child_node.content:
                        padding = " " * (tree_width - len(base_line))
                        generator_info = f"{padding} │ 🤖 {child_node.content}"
                else:
                    # Handle regular files with generators
                    generator = None
                    if child_node.xattrs:
                        if "generator" in child_node.xattrs:
                            generator = child_node.xattrs["generator"]
                        elif child_node.xattrs.get("generate_content") == "true":
                            generator = "default"
                    
                    if generator:
                        padding = " " * (tree_width - len(base_line))
                        generator_info = f"{padding} │ 🔄 {generator}"
                        
                        # For default generator, show prompt and model info more concisely
                        if generator == "default":
                            prompt_path = find_nearest_prompt_file(child_path, structure)
                            model_path = find_nearest_model_file(child_path, structure)
                            
                            # Show relative paths more concisely
                            rel_prompt = os.path.basename(prompt_path) if prompt_path else "prompt.default"
                            rel_model = os.path.basename(model_path) if model_path else "model.default"
                            
                            # Add model and prompt info if available
                            model_info = ""
                            prompt_info = ""
                            
                            if model_path and model_path in structure:
                                model_node = self._convert_to_filenode(structure[model_path])
                                if model_node.content:
                                    model_info = f"[{model_node.content.strip()}]"
                            
                            if prompt_path and prompt_path in structure:
                                prompt_node = self._convert_to_filenode(structure[prompt_path])
                                if prompt_node.content:
                                    excerpt = get_prompt_excerpt(prompt_node.content, 40)
                                    prompt_info = f"「{excerpt}」"
                            
                            # Construct final info line with emojis - model first, then prompt
                            model_part = f"🤖 {rel_model}"
                            if model_info:
                                model_part += f" {model_info}"
                            
                            prompt_part = f"📝 {rel_prompt}"
                            if prompt_info:
                                prompt_part += f" {prompt_info}"
                            
                            generator_info += f" using {model_part}, {prompt_part}"
            
            # Add this node
            result.append(f"{base_line}{generator_info}")
            
            # Recursively add children if this is a directory
            if child_node.type == "directory":
                result.extend(self._build_tree(child_path, structure, child_indent, dimensions))
        
        return result
    
    def generate(self, path: str, node: FileNode, fs_structure: Dict[str, Any]) -> str:
        """Generate a structured tree visualization of the filesystem."""
        # Add header with improved formatting
        header = """# Filesystem Tree Structure
#
# File Types:
#   🤖 .model files  - Specifies AI model configuration
#   📝 .prompt files - Contains generation instructions
#   🔄 Generated    - Content created on-demand
#
# For generated files:
#   - Shows which generator is responsible (e.g., 'default', 'tree', etc.)
#   - For default generator, displays:
#     • The model configuration in [brackets]
#     • Which model and prompt files are being used
#     • Prompt excerpt in 「quotes」
#
# Tree Structure                                    Generator Information
# --------------                                    ---------------------
"""
        # Calculate dimensions for alignment
        tree_width, info_width = self._calculate_dimensions("/", fs_structure)
        tree_width = max(tree_width, 45)  # Minimum width for readability
        
        # Build tree starting from root
        tree_lines = self._build_tree("/", fs_structure, dimensions=(tree_width, info_width))
        
        return header + "\n".join(tree_lines) + "\n"
