import os
import shutil
import subprocess

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def create_project(project_name):
    """Create a new KivyMD project."""
    project_path = os.path.join(os.getcwd(), project_name)
    if os.path.exists(project_path):
        print(f"Error: Directory '{project_name}' already exists.")
        return

    os.makedirs(project_path)
    shutil.copytree(TEMPLATE_DIR, project_path, dirs_exist_ok=True)

    print(f"Project '{project_name}' created successfully.")


def add_screen(screen_name):
    """Add a new screen to the project."""
    project_path = os.getcwd()
    screens_path = os.path.join(project_path, "screens", screen_name)

    if os.path.exists(screens_path):
        print(f"Error: Screen '{screen_name}' already exists.")
        return

    # Copy screen template
    shutil.copytree(os.path.join(TEMPLATE_DIR, "screen_template"), screens_path)

    # Update main_router.py
    router_path = os.path.join(project_path, "core", "main_router.py")
    with open(router_path, "a") as router_file:
        router_file.write(
            f"\nfrom screens.{screen_name}.screen import Screen as {screen_name.capitalize()}Screen"
        )
        router_file.write(
            f"\nself.add_widget({screen_name.capitalize()}Screen(name='{screen_name}'))"
        )

    print(f"Screen '{screen_name}' added successfully.")
