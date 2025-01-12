
# mhmixtools

This package provides various automation tools for developers.

## Current Features
- **template_sync**: Automate HTML template updates.
- **folder_structure_generator**: Simplify the creation of project folder structures.
- **image_utils**: Utilities for image processing tasks.
- **decorators**: Handy decorators for Python functions.

---

## Installation
To install the package, use the following command:

```bash
pip install mhmixtools
```

---

## Usage Guide

### 1. `template_sync`

This module helps automate updating multiple HTML files with a shared template.  

#### Available Functions:
1. **`list_html`**  
   Lists all `.html` files in a project, with options to exclude specific directories and display the results.

   **Function Signature**:
   ```python
   list_html(exclude_dirs: list, show: bool = True) -> list
   ```
   - **Parameters**:
     - `exclude_dirs` (list): Directories to skip while searching for `.html` files.
     - `show` (bool): When `True` (default), prints the file locations to the terminal. When `False`, returns a list of file paths.
   - **Returns**:
     - A list of file paths if `show=False`.

   **Example**:
   ```python
   from mhmixtools.template_sync import list_html

   # List HTML files excluding the 'env' directory and print the results
   list_html(exclude_dirs=['env'])

   # Get a list of HTML file paths
   html_files = list_html(exclude_dirs=['env'], show=False)
   print(html_files)
   ```

2. **`render_templates`**  
   Updates multiple HTML files by applying a shared template, preserving dynamic content within a specific container.

   **Function Signature**:
   ```python
   render_templates(template_url: str, target_files: list, content_id: str, indent: int = 4)
   ```
   - **Parameters**:
     - `template_url` (str): Path to the shared template file.
     - `target_files` (list): List of file paths to be updated with the template.
     - `content_id` (str): The `id` of the container element holding dynamic content. Content within this container remains unchanged.
     - `indent` (int): Indentation level for prettifying the HTML output (default is 4 spaces).
   - **Returns**:
     - None. Updates are made directly to the target files.

   **Example**:
   ```python
   from mhmixtools.template_sync import render_templates

   # Define the template file and target files
   template_url = "template.html"
   target_files = [
       "file1.html",
       "file2.html",
   ]

   # Define the dynamic content container's ID
   content_id = "content"

   # Apply the template with 4-space indentation
   render_templates(template_url, target_files, content_id, indent=4)
   ```

---

### Notes
- Ensure the `content_id` matches the `id` attribute of the dynamic content container in your HTML files.
- Use `list_html` to quickly gather all target file paths.

---
