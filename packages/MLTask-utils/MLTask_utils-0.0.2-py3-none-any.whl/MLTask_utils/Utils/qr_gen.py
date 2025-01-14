import qrcode
from PIL import Image
import random
import os

image_size = 10  # 210x210
image_size = 20  # 420x420
image_size = 24  # 504x504
image_size = 25  # 504x504

script_directory = os.path.dirname(__file__)


def generate_qr_code(qr_data="https://mltask.com/", directory=None, filename='generated_qr.png'):
    img = qrcode.make(qr_data)
    final_directory = directory if directory is not None else script_directory
    saved_filepath = f"{final_directory}/{filename}"
    img.save(saved_filepath)
    return saved_filepath


def generate_qr_code_complex(qr_data="https://mltask.com/"):
    try:
        qr_images_output_dir = os.path.join(script_directory, "qr_images")
        if not os.path.exists(qr_images_output_dir):
            os.makedirs(qr_images_output_dir)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        # Number of steps for the progressive reveal
        n_steps = 30
        # Generate and save a series of images showing progressive reveal

        # Get the dimensions of the QR code
        qr_width = qr.modules_count * image_size
        qr_height = qr.modules_count * image_size

        # Create a blank white image
        img = Image.new("RGB", (qr_width, qr_height), "white")
        coordinates = [(x, y) for y in range(qr.modules_count)
                       for x in range(qr.modules_count)]

        random.shuffle(coordinates)
        counter = 0
        progress_chunk = 1 / n_steps
        current_step = 1
        accumulated_progress = 0
        all_coors_length = len(coordinates)
        for (x, y) in coordinates:
            counter += 1
            progress = counter / all_coors_length

            if qr.modules[x][y]:
                fill_color = "black"
            else:
                fill_color = "white"
            draw_x = x * image_size
            draw_y = y * image_size

            draw = Image.new("RGB", (image_size, image_size), fill_color)
            img.paste(draw, (draw_x, draw_y))
            # print(progress)
            if progress >= accumulated_progress:
                print(f"{current_step} {accumulated_progress}")
                accumulated_progress += progress_chunk
                img.save(f"{qr_images_output_dir}/step_{current_step:02}.png")
                current_step += 1

        filename = f"{qr_images_output_dir}/step_{current_step - 1:02}.png"
        img.save(filename)
        # repeat generated image
        qr_images_output_dir = os.path.join(script_directory, "qr_repeat")
        if not os.path.exists(qr_images_output_dir):
            os.makedirs(qr_images_output_dir)

        for step in range(n_steps):
            img.save(f"{qr_images_output_dir}/step_repeat_{step:02}.png")

        # Generate and save a series of images showing progressive reveal
        qr_images_output_dir = os.path.join(script_directory, "qr_brightness")
        if not os.path.exists(qr_images_output_dir):
            os.makedirs(qr_images_output_dir)

        for step in range(n_steps):
            step_image = generate_progress_image(
                n_steps, step, qr.modules_count, qr.modules)
            step_image.save(
                f"{qr_images_output_dir}/step_bright_{step:02}.png")
        print("Images generated successfully!")

    except Exception as e:
        # Generic exception handling (catches any other exceptions)
        print("An error occurred:", e)
    finally:
        # Optional: Code that always runs, regardless of whether an exception occurred
        print("Finally block: This code always executes")


# Function to generate an intermediate image with a certain progress
def generate_progress_image(n, step, qr_modules_count, qr_modules):

    # Create a blank white image
    img = Image.new("RGB", (qr_modules_count * image_size,
                    qr_modules_count * image_size), "white")

    # Iterate over the QR code's modules and fill them progressively
    for y in range(qr_modules_count):
        for x in range(qr_modules_count):
            if qr_modules[x][y]:
                fill_color = "black"
            else:
                fill_color = "white"

            # Calculate the position to draw
            draw_x = x * image_size
            draw_y = y * image_size

            # Create a drawing context and fill the module
            draw = Image.new("RGB", (image_size, image_size), fill_color)
            img.paste(draw, (draw_x, draw_y))

    # Adjust the progress
    progress = min(step / n, 1)

    # Create an image with the correct progress level
    final_image = Image.blend(
        Image.new("RGB", img.size, "white"), img, progress)

    return final_image
