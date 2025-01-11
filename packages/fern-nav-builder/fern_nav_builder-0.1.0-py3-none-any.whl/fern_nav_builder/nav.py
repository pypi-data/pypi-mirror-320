import os
import sys
import yaml
from pathlib import Path

def create_nested_structure(file_paths):
    # Initialize the root structure
    sections = {}

    # Process each file
    for file_path in file_paths:
        # Get the filename without extension
        filename = Path(file_path).stem
        # Split the filename by hyphens
        parts = filename.split('-')
        
        # Navigate/create the nested structure
        current_level = sections
        for i, part in enumerate(parts[:-1]):  # All parts except the last one are sections
            if part not in current_level:
                current_level[part] = {'section': part, 'contents': []}
            current_level = current_level[part]['contents']
        
        # Add the page to the deepest section
        if parts:
            # If there's only one part, add it as a top-level page
            if len(parts) == 1:
                sections[parts[0]] = {
                    'page': parts[0],
                    'path': f'pages/{file_path}'  # Removed ./ prefix
                }
            else:
                # Add the page to the deepest section's contents
                current_level.append({
                    'page': parts[-1],
                    'path': f'pages/{file_path}'  # Removed ./ prefix
                })

    # Convert the sections dict to the required format
    navigation = []
    for key, value in sections.items():
        if 'section' in value:
            navigation.append(value)
        else:
            # Handle top-level pages
            navigation.append(value)

    return navigation

def create_docs_yml(folder_path):
    # Get all markdown files in the folder
    markdown_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md') or file.endswith('.mdx'):
                # Make path relative to the pages directory
                relative_path = os.path.relpath(os.path.join(root, file), folder_path)
                markdown_files.append(relative_path)

    # Create the navigation structure
    navigation = create_nested_structure(markdown_files)

    # Create the full docs.yml structure according to Fern's format
    docs_structure = {
        'instances': [{
            'url': 'docs.example.com'  # This should be configured by the user
        }],
        'navigation': navigation
    }

    # Write to docs.yml one directory up from the pages folder
    output_path = os.path.join(os.path.dirname(folder_path), 'docs.yml')
    with open(output_path, 'w') as f:
        yaml.dump(docs_structure, f, sort_keys=False, allow_unicode=True)

    print(f"docs.yml has been created at {output_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: fern-nav <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    create_docs_yml(folder_path)

if __name__ == "__main__":
    main()
