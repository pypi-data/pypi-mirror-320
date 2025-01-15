import sys

from kivymd_admin.utils import add_screen, create_project


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  startproject <project_name>  - Create a new KivyMD project")
        print("  addscreen <screen_name>      - Add a new screen to the project")
        return

    command = sys.argv[1]

    if command == "startproject":
        if len(sys.argv) < 3:
            print("Error: Please provide a project name.")
            return
        project_name = sys.argv[2]
        create_project(project_name)
    elif command == "addscreen":
        if len(sys.argv) < 3:
            print("Error: Please provide a screen name.")
            return
        screen_name = sys.argv[2]
        add_screen(screen_name)
    else:
        print(f"Unknown command: {command}")
