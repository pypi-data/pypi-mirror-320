import subprocess


def get_container_name():
    command = "cat /etc/hostname"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if error:
        print(f"An error occurred: {error.decode('utf-8')}")
        return None

    return output.decode('utf-8').strip()

def get_copy_command(output_path):
    return f"docker cp {get_container_name()}:/var/task/{output_path} ~/Downloads"