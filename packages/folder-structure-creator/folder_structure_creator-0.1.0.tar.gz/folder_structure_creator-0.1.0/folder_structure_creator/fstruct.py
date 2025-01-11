# folder_structure_creator/fstruct.py

import os
import sys

def create_folder_structure_from_file(file_path, base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(file_path)

    with open(file_path, "r") as file:
        folder_structure = file.read().splitlines()
    
    path_stack = [base_dir]
    for line in folder_structure:
        if not line.strip():
            continue
        indent_level = len(line) - len(line.lstrip())
        folder_name = line.strip()

        # Ensure path_stack has the correct length for the current indent level
        path_stack = path_stack[:indent_level + 1]
        current_path = os.path.join(path_stack[-1], folder_name)
        path_stack.append(current_path)

        # Debug statement to print the current path
        print(f"Creating folder: {current_path}")

        os.makedirs(current_path, exist_ok=True)

def main():
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all .txt files in the executable directory
    txt_files = [f for f in os.listdir(exe_dir) if f.endswith('.txt')]
    
    if not txt_files:
        print("No .txt files found in the directory.")
        return
    
    # If there's only one .txt file, use it. Otherwise, let the user choose
    if len(txt_files) == 1:
        file_path = os.path.join(exe_dir, txt_files[0])
    else:
        print("Multiple .txt files found. Please choose one:")
        for i, file_name in enumerate(txt_files, 1):
            print(f"{i}: {file_name}")
        choice = int(input("Enter the number of the file you want to use: "))
        file_path = os.path.join(exe_dir, txt_files[choice - 1])
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    print(f"Using file path: {file_path}")
    
    create_folder_structure_from_file(file_path)
    print("Folder structure created successfully!")

if __name__ == "__main__":
    main()
