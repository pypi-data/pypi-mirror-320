
import ast, os, pyminify

def list_python_files():
    return [f for f in os.listdir('.') if f.endswith('.py')]
# Function to minify Python code
def minify_code(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        # Parse the code into an abstract syntax tree (AST)
        tree = ast.parse(code)
        # Remove type annotations
        class RemoveAnnotations(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                node.returns = None
                node.args.args = [
                    ast.arg(arg=arg.arg, annotation=None) for arg in node.args.args
                ]
                return self.generic_visit(node)
        tree = RemoveAnnotations().visit(tree)
        ast.fix_missing_locations(tree)
        # Convert the modified ast back to source code (use pyminify)
        minified_code = pyminify.to_source(tree)
        # Remove comments and extra blank lines
        minified_code = '\n'.join(
            line for line in minified_code.splitlines() if line.strip() and not line.strip().startswith('#')
        )
        # Save the minified code to a new file
        minified_file = f"minified_{os.path.basename(file_path)}"
        with open(minified_file, 'w', encoding='utf-8') as file:
            file.write(minified_code)
        print(f"Minified file saved as: {minified_file}")
    except Exception as e:
        print(f"Error while minifying the file: {e}")

if __name__ == "__main__":
    print("Please opt:\n1. select a py file to minify\n2. minify all py file(s) in the current directory")
    choice = input("Enter your choice (1 to 2): ")

    if choice=="1":
        # option 1: minify a selected py file
        python_files = list_python_files()
        if not python_files:
            print("No Python files found in the current directory.")
        else:
            print("Available Python files:")
            for idx, file in enumerate(python_files, start=1):
                print(f"{idx}. {file}")
            try:
                choice = int(input("Enter the number of the file you want to minify: "))
                if 1 <= choice <= len(python_files):
                    selected_file = python_files[choice - 1]
                    minify_code(selected_file)
                else:
                    print("Invalid choice. Please select a valid file number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    elif choice=="2":
        # option 2: minify all the py file(s) in the current directory
        python_files = list_python_files()

        if not python_files:
            print("No Python files found in the current directory.")
        else:
            print("Minifying all Python files in the current directory...")
            for file in python_files:
                minify_code(file)
            print("All files have been minified.")
    else:
        print("Not a valid number.")