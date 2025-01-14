import os
import shutil
import pickle


def get_file_extension(file_path):
    _, extension = os.path.splitext(file_path)
    return extension


def save_text_to_file(
    text, destination_folder, filename_without_extension, file_extension=".txt"
):
    os.makedirs(destination_folder, exist_ok=True)

    destination_path = os.path.join(
        destination_folder,
        filename_without_extension + file_extension,
    )
    with open(destination_path, "w") as f:
        # Write the text to the file
        f.write(text)
    return os.path.abspath(destination_path)


def copy_file(source_path, destination_path):
    try:
        shutil.copy(source_path, destination_path)
        destination_file = os.path.join(destination_path, os.path.basename(source_path))
        print(f"File copied from '{source_path}' to '{destination_path}' successfully.")
        return destination_file
    except FileNotFoundError:
        print("File not found. Please check the source path.")
    except PermissionError:
        print("Permission denied. Please check permissions or destination path.")
    except Exception as e:
        print(f"An error occurred: {e}")


def save_dict_to_file(data, filename, folder_name="streamCache"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    with open(f"{folder_name}/{filename}", "wb") as file:
        pickle.dump(data, file)


def load_dict_from_file(filename, folder_name="streamCache"):
    try:
        with open(f"{folder_name}/{filename}", "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        print(f"The file '{filename}' does not exist. Creating a new file.")
        empty_dict = {}
        save_dict_to_file(empty_dict, filename)
        return empty_dict
