import os
import shutil


def copy_static_to_public(source_dir: str, destination_dir: str) -> None:
    if os.path.exists(destination_dir):
        shutil.rmtree(destination_dir)

    copy_directory(source_dir, destination_dir)


def copy_directory(source_dir: str, destination_dir: str) -> None:
    os.mkdir(destination_dir)

    for filename in os.listdir(source_dir):
        source_path = os.path.join(source_dir, filename)
        destination_path = os.path.join(destination_dir, filename)

        if os.path.isdir(source_path):
            copy_directory(source_path, destination_path)
        else:
            print(f"Copying {source_path} to {destination_path}")
            shutil.copy(source_path, destination_path)


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_dir = os.path.join(project_root, "static")
    destination_dir = os.path.join(project_root, "public")
    copy_static_to_public(source_dir, destination_dir)

if __name__ == "__main__":
    main()