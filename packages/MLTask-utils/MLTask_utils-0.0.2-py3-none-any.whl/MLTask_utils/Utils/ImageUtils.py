import glob
from PIL import Image
from typing import List
import os
import cv2
import numpy as np
from scipy.cluster import vq


def shrink_image_by_percent(input_image_path, reduction_percentage=0.1):
    original_image = Image.open(input_image_path)
    width, height = original_image.size

    # Calculate the new width and height based on the reduction percentage
    new_width = int(width * (1 - reduction_percentage))
    new_height = int(height * (1 - reduction_percentage))

    # Resize the image while maintaining aspect ratio
    resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)

    # Save the resized image
    resized_image.save(input_image_path)


def reduce_image_size(image_path, target_size_kb):
    # Check the initial size of the image
    initial_size_kb = os.path.getsize(image_path)  # Get size in KB
    if initial_size_kb <= target_size_kb:
        print(
            f"The initial size {initial_size_kb} of the image is already under {target_size_kb} KB."
        )
        return

    img = Image.open(image_path)

    while True:
        size_kb = os.path.getsize(image_path)  # Get size in KB

        if size_kb <= target_size_kb:
            break  # If the size is under the target, exit the loop
        else:
            shrink_image_by_percent(image_path, 0.05)

    print(f"Final size of the image: {size_kb} KB")


def make_gif_from_folder(
    frame_folder, frame_duration, extension="png", output_filename="output.gif", loop=0
):
    frames = [Image.open(image) for image in glob.glob(f"{frame_folder}/*.{extension}")]
    save_gif(
        frames=frames,
        frame_duration=frame_duration,
        output_filename=output_filename,
        loop=loop,
    )


def make_gif_from_filenames(
    image_filenames: List[str], frame_duration, output_filename="output.gif", loop=0
):
    frames = []
    for filename in image_filenames:
        img = Image.open(filename)
        frames.append(img)
    save_gif(
        frames=frames,
        frame_duration=frame_duration,
        output_filename=output_filename,
        loop=loop,
    )


def save_gif(
    frames: List[Image.Image], frame_duration, output_filename="output.gif", loop=0
):
    frames[0].save(
        output_filename,
        format="GIF",
        append_images=frames[1:],
        save_all=True,
        duration=frame_duration,  # Duration between frames in milliseconds
        loop=loop,
    )


def crop_to_square(image_path, destination_path=None):
    """
    Crops an image from the center to a square and returns the new image path.

    Args:
        image_path (str): The path to the input image file.
        destination_path (str, optional): The destination path for the cropped image. If not provided,
            the cropped image will be saved in the same directory as the original image with "_crop_square" added to the filename.

    Returns:
        str: The path of the cropped image.

    Raises:
        ValueError: If the input image file does not exist or is not supported.

    """

    # Check if the image file exists
    if not os.path.isfile(image_path):
        raise ValueError("Input image file does not exist: {}".format(image_path))

    # Open the image
    image = Image.open(image_path)

    # Calculate the crop dimensions
    width, height = image.size
    size = min(width, height)
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size

    # Crop the image
    cropped_image = image.crop((left, top, right, bottom))

    # Set the destination path if not provided
    if destination_path is None:
        filename, ext = os.path.splitext(image_path)
        destination_path = filename + "_crop_square" + ext

    # Save the cropped image
    cropped_image.save(destination_path)
    cropped_image.close()

    return destination_path


def convert_to_jpg(image_path, destination_path=None):
    """
    Converts an image to JPG format if it is in PNG format.

    Args:
        image_path (str): The path to the input image file.
        destination_path (str, optional): The destination path for the converted image. If not provided,
            the converted image will be saved in the same directory as the original image with a new extension.

    Returns:
        str: The path of the converted image.

    Raises:
        ValueError: If the input image file does not exist or is not supported.

    """

    # Check if the image file exists
    if not os.path.isfile(image_path):
        raise ValueError("Input image file does not exist: {}".format(image_path))

    # Check if the image is in PNG format
    if image_path.lower().endswith(".png"):
        # Load the image
        image = Image.open(image_path)

        # Convert to JPG format
        if destination_path is None:
            destination_path = os.path.splitext(image_path)[0] + ".jpg"

        image = image.convert("RGB")
        image.save(destination_path, "JPEG")
        image.close()

        return destination_path

    # If the image is already in JPG format or has a different format, return the original image path
    return image_path


def blur_image(input_image_path, output_image_path, blur_strength):
    # Read the input image
    image = cv2.imread(input_image_path)

    if blur_strength % 2 == 0:
        blur_strength += 1  # If even, make it odd by adding 1

    # Apply Gaussian blur
    blurred_image = cv2.GaussianBlur(image, (blur_strength, blur_strength), 0)

    # Save the blurred image
    cv2.imwrite(output_image_path, blurred_image)
    return os.path.abspath(output_image_path)


def get_dominant_color(image_path):
    """
    Gets the dominant color from an image path.

    Args:
        image_path: Path to the image file.

    Returns:
        A string representing the most dominant color in RGB hex format (#RRGGBB).
    """

    # Open the image and optionally resize for faster processing
    img = Image.open(image_path)
    img = img.resize((150, 150), Image.LANCZOS)  # Optional resizing

    # Convert the image to a NumPy array
    arr = np.asarray(img)

    # Reshape the array to flatten it
    shape = arr.shape
    arr = arr.reshape(np.product(shape[:2]), shape[2]).astype(float)

    # Define the number of clusters (adjust as needed)
    num_clusters = 5

    # Perform k-means clustering to find dominant colors
    codes, _ = vq.kmeans(arr, num_clusters)

    # Get the histogram to find the most frequent cluster
    vecs, _ = vq.vq(arr, codes)
    counts, _ = np.histogram(vecs, len(codes))
    index_max = np.argmax(counts)

    # Get the color value from the most frequent cluster center
    peak = codes[index_max]
    color = tuple(int(max(0, min(255, x))) for x in peak)

    return color
