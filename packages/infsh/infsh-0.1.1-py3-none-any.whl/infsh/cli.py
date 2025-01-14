import os
import sys
import json
import importlib.util
import yaml
from infsh import BaseApp, BaseAppInput, BaseAppOutput

# Import default template contents
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
DEFAULT_TEMPLATES = {
    ".gitignore": None,
    "inf.yml": None, 
    "inference.py": None,
    "openapi.json": None
}

# Load all template contents
for template in DEFAULT_TEMPLATES:
    with open(os.path.join(TEMPLATES_DIR, template)) as f:
        DEFAULT_TEMPLATES[template] = f.read()

def generate_init_py():
    """Generate __init__.py if it doesn't exist."""
    if os.path.exists("__init__.py"):
        print("» __init__.py already exists, skipping...")
        return False
    
    print("» Creating __init__.py...")
    with open("__init__.py", "w") as f:
        f.write("")
    print("✓ Created __init__.py")
    return True

def generate_yaml():
    """Generate inf.yml if it doesn't exist."""
    if os.path.exists("inf.yml"):
        with open("inf.yml", "r") as f:
            config = yaml.safe_load(f)
        print(f"» inf.yml already exists with name: {config['name']}")
        return False
    
    print("» Creating inf.yml...")
    with open("inf.yml", "w") as f:
        f.write(DEFAULT_TEMPLATES["inf.yml"].strip())
    print("✓ Created inf.yml")
    return True

def generate_inference():
    """Generate inference.py if it doesn't exist."""
    if os.path.exists("inference.py"):
        print("» inference.py already exists, skipping...")
        return False
    
    print("» Creating inference.py...")
    with open("inference.py", "w") as f:
        f.write(DEFAULT_TEMPLATES["inference.py"].strip())
    print("✓ Created inference.py")
    return True

def generate_requirements():
    """Generate requirements.txt if it doesn't exist."""
    if os.path.exists("requirements.txt"):
        print("» requirements.txt already exists, skipping...")
        return False
    
    print("» Creating requirements.txt...")
    with open("requirements.txt", "w") as f:
        f.write("pydantic>=2.0.0\n")
    print("✓ Created requirements.txt")
    return True

def generate_gitignore():
    """Generate .gitignore if it doesn't exist."""
    if os.path.exists(".gitignore"):
        print("» .gitignore already exists, skipping...")
        return False
    
    print("» Creating .gitignore...")
    with open(".gitignore", "w") as f:
        f.write(DEFAULT_TEMPLATES[".gitignore"].strip())
    print("✓ Created .gitignore")
    return True

def generate_default_openapi():
    """Generate openapi.json if it doesn't exist."""
    if os.path.exists("openapi.json"):
        print("» openapi.json already exists, skipping...")
        return False
    
    print("» Creating openapi.json...")
    with open("openapi.json", "w") as f:
        f.write(DEFAULT_TEMPLATES["openapi.json"].strip())
    print("✓ Created openapi.json")
    return True

def create_app():
    """Create a new inference.sh application."""
    generate_yaml()
    generate_inference()
    generate_requirements()
    generate_gitignore()
    generate_default_openapi()
    print("\n✓ Successfully created new inference.sh app structure!")

def login():
    """Login to inference.sh (dummy implementation)."""
    # Dummy implementation
    print("✓ Logged in as: test_user")
    return "test_user"

def generate_openapi_schema(module) -> dict:
    """Generate OpenAPI schema from AppInput and AppOutput models."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "inference.sh API", "version": "1.0.0"},
        "paths": {
            "/predict": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": module.AppInput.model_json_schema()
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful prediction",
                            "content": {
                                "application/json": {
                                    "schema": module.AppOutput.model_json_schema()
                                }
                            }
                        }
                    }
                }
            }
        }
    }

def predeploy():
    """Run predeploy checks and generate OpenAPI schema."""
    try:
        # Generate missing files if needed
        if not os.path.exists("inf.yml"):
            generate_yaml()
        if not os.path.exists("inference.py"):
            generate_inference()
        if not os.path.exists("requirements.txt"):
            generate_requirements()
        if not os.path.exists(".gitignore"):
            generate_gitignore()

        # Use the context manager to handle imports
        with TemporaryPackageStructure() as module:
            print("✓ inference.py successfully imported")
            
            # Check required classes and methods
            inference_app = module.App()
            if not all(hasattr(inference_app, method) for method in ['setup', 'run', 'unload']):
                print("✗ App must implement setup, run, and unload methods")
                return False
            print("✓ App implements required methods: setup, run, unload")

            # Verify App is a valid class
            if not isinstance(module.App, type) or not issubclass(module.App, BaseApp):
                print("✗ App must be a class that inherits from BaseApp")
                return False
            print("✓ App class inherits from BaseApp")

            # Verify AppInput and AppOutput are valid models
            if not (isinstance(module.AppInput, type) and issubclass(module.AppInput, BaseAppInput)):
                print("✗ AppInput must inherit from BaseAppInput")
                return False
            print("✓ AppInput model inherits from BaseAppInput")
            if not (isinstance(module.AppOutput, type) and issubclass(module.AppOutput, BaseAppOutput)):
                print("✗ AppOutput must inherit from BaseAppOutput")
                return False
            print("✓ AppOutput model inherits from BaseAppOutput")

            # Generate OpenAPI schema
            schema = generate_openapi_schema(module)
            
            with open("openapi.json", "w") as f:
                json.dump(schema, f, indent=2)
            print("✓ OpenAPI schema generated successfully")

            print("\n✓ All predeploy checks passed")
            return True

    except Exception as e:
        print("\n✗ Predeploy failed:")
        print(f"✗ Type: {type(e).__name__}")
        print(f"✗ Message: {str(e)}")
        
        import traceback
        print("\n» Traceback:")
        traceback.print_exc()
        return False
    
def deploy():
    """Deploy the app to inference.sh."""
    predeploy()
    print("» Starting deployment process...")
    # Check if git is initialized
    if not os.path.exists(".git"):
        print("✗ Git repository not initialized. Please run 'git init' first")
        return False
    
    # Check if there are any changes to commit
    import subprocess
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if status.stdout:
        print("✗ Uncommitted changes detected. Please commit all changes before deploying")
        return False
        
    # Check if remote exists
    try:
        subprocess.run(["git", "remote", "get-url", "origin"], check=True)
        print("✓ Remote repository configured")
    except subprocess.CalledProcessError:
        print("✗ Remote repository not found. Please run 'git remote add origin <your-repo-url>' first")
        return False

    try:
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        print("✓ Code pushed to remote repository")
    except subprocess.CalledProcessError:
        print("✗ Failed to push to remote repository. Please check your git configuration")
        return False
    print("✓ Application deployed successfully")
    return True

class TemporaryPackageStructure:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.infsh_dir = os.path.join(self.current_dir, ".infsh")
        self.temp_dir = os.path.join(self.infsh_dir, "build")
        self.module = None

    def __enter__(self):
        # Create .infsh/build structure
        os.makedirs(self.temp_dir, exist_ok=True)
            
        # Copy entire directory contents
        import shutil
        for item in os.listdir(self.current_dir):
            # Skip .infsh directory and any other hidden files/directories
            if item.startswith('.'):
                continue
                
            source = os.path.join(self.current_dir, item)
            destination = os.path.join(self.temp_dir, item)
            
            if os.path.isdir(source):
                if os.path.exists(destination):
                    shutil.rmtree(destination)
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
        
        # Create __init__.py if it doesn't exist
        init_path = os.path.join(self.temp_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                pass
            
        # Add both the build directory and its parent to sys.path
        if self.temp_dir not in sys.path:
            sys.path.insert(0, self.temp_dir)
        if self.infsh_dir not in sys.path:
            sys.path.insert(0, self.infsh_dir)
            
        # Import module
        spec = importlib.util.spec_from_file_location(
            "build.inference",
            os.path.join(self.temp_dir, "inference.py")
        )
        if not spec or not spec.loader:
            raise ImportError("Cannot load inference.py")
            
        self.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.module
        spec.loader.exec_module(self.module)
        
        return self.module

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up build directory but keep .infsh
        import shutil
        shutil.rmtree(self.temp_dir)
        if "build.inference" in sys.modules:
            del sys.modules["build.inference"]
