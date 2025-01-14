import requests
import random
import os
import io
import warnings
from tqdm import tqdm
from PIL import Image
import uuid

from stability_sdk import client, api
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from stability_sdk.animation import AnimationArgs, Animator
from stability_sdk.utils import create_video_from_frames

# os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
STABILITY_HOST = "grpc.stability.ai:443"
STABILITY_KEY = os.environ.get('STABILITY_API_KEY')


def text_to_image_sd3(prompt, seed=0, aspect_ratio="1:1", model="sd3", negative_prompt=None):
    data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "model": model,
        "seed": seed,
        "aspect_ratio": aspect_ratio,
        "output_format": "png",
    }
    if negative_prompt != None and len(negative_prompt) > 0:
        data["negative_prompt"] = negative_prompt

    response = requests.post(
        f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
        headers={
            "authorization": f"Bearer {STABILITY_KEY}",
            "accept": "image/*"
        },
        files={"none": ''},
        data=data,
    )

    if response.status_code == 200:
        file_path = '/tmp/' + str(uuid.uuid4()) + ".png"
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return [file_path]

    else:
        raise Exception(str(response.json()))


def text_to_image(prompt, seed=-1, steps=30, cfg_scale=8, width=512, height=512, samples=1, sampler=generation.SAMPLER_K_DPMPP_2M, style_preset=None):

    # Set up our connection to the API.
    stability_api = client.StabilityInference(
        key=STABILITY_KEY,  # API Key reference.
        verbose=True,  # Print debug messages.
        # Set the engine to use for generation.
        engine="stable-diffusion-xl-1024-v1-0",
        # engine="stable-diffusion-xl-1024-v0-9",
        # Available engines: stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0
        # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-diffusion-xl-beta-v2-2-2 stable-inpainting-v1-0 stable-inpainting-512-v2-0
    )

    # Set up our initial generation parameters.
    answers = stability_api.generate(
        prompt,
        # If a seed is provided, the resulting generated image will be deterministic.
        seed=random.randint(1, 2**31) if seed == -1 else seed,
        # What this means is that as long as all generation parameters remain the same, you can always recall the same image simply by generating it again.
        # Note: This isn't quite the case for CLIP Guided generations, which we tackle in the CLIP Guidance documentation.
        # Amount of inference steps performed on image generation. Defaults to 30.
        steps=steps,
        # Influences how strongly your generation is guided to match your prompt.
        cfg_scale=cfg_scale,
        # Setting this value higher increases the strength in which it tries to match your prompt.
        # Defaults to 7.0 if not specified.
        width=width,  # Generation width, defaults to 512 if not included.
        height=height,  # Generation height, defaults to 512 if not included.
        # Number of images to generate, defaults to 1 if not included.
        samples=samples,
        # Choose which sampler we want to denoise our generation with.
        sampler=sampler,

        # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
        # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m, k_dpmpp_sde)
        style_preset=style_preset
        # Enum: "enhance" "anime" "photographic" "digital-art" "comic-book" "fantasy-art" "line-art" "analog-film" "neon-punk" "isometric" "low-poly" "origami" "modeling-compound" "cinematic" "3d-model" "pixel-art" "tile-texture"
    )

    # Set up our warning to print to the console if the adult content classifier is tripped.
    # If adult content classifier is not tripped, save generated images.
    images_paths = []
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                # Save our generated images with their seed number as the filename.
                file_path = '/tmp/' + str(artifact.seed) + ".png"
                img.save(file_path)
                images_paths.append(file_path)

    return images_paths


def upscale_image(image_file_path, upscale_output_path="/", upscaled_image_name="imageupscaled"):
    stability_api = client.StabilityInference(
        key=STABILITY_KEY,  # API Key reference.
        upscale_engine="esrgan-v1-x2plus",
        # Available Upscaling Engines: esrgan-v1-x2plus, stable-diffusion-x4-latent-upscaler
        verbose=True,  # Print debug messages.
    )
    img = Image.open(image_file_path)

    answers = stability_api.upscale(
        # Pass our image to the API and call the upscaling process.
        init_image=img,
        # width=1024, # Optional parameter to specify the desired output width.
        # prompt="A beautiful sunset", # Optional parameter when using `stable-diffusion-x4-latent-upscaler` to specify a prompt to use for the upscaling process.
        # seed=1234, # Optional parameter when using `stable-diffusion-x4-latent-upscaler` to specify a seed to use for the upscaling process.
        # steps=20, # Optional parameter when using `stable-diffusion-x4-latent-upscaler` to specify the number of diffusion steps to use for the upscaling process. Defaults to 20 if no value is passed, with a maximum of 50.
        # cfg_scale=7 # Optional parameter when using `stable-diffusion-x4-latent-upscaler` to specify the strength of prompt in use for the upscaling process. Defaults to 7 if no value is passed.
    )
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please submit a different image and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                big_img = Image.open(io.BytesIO(artifact.binary))
                # Save our image to
                big_img.save(f"{upscale_output_path}{upscaled_image_name}.png")


def text_to_animation(animation_prompts={
    0: "a photo of a cute cat",
    5: "a photo of a cute ragdoll cat",
}, negative_prompt="", max_frames=10, seed=-1, interpolate_prompts=True, locked_seed=True, frame_suffix="frame_", out_dir="video_01", video_output_filename="video"):

    context = api.Context(STABILITY_HOST, STABILITY_KEY)
    # Configure the animation
    args = AnimationArgs()
    args.interpolate_prompts = interpolate_prompts
    args.locked_seed = locked_seed
    args.max_frames = max_frames
    args.seed = random.randint(1, 2**31) if seed == -1 else seed
    args.strength_curve = "0:(0)"
    args.diffusion_cadence_curve = "0:(4)"
    args.cadence_interp = "film"
    # Create Animator object to orchestrate the rendering
    animator = Animator(
        api_context=context,
        animation_prompts=animation_prompts,
        negative_prompt=negative_prompt,
        args=args
    )

    # Render each frame of animation
    for idx, frame in enumerate(animator.render()):
        frame.save(f"{frame_suffix}{idx:05d}.png")

    animator = Animator(
        api_context=context,
        animation_prompts=animation_prompts,
        negative_prompt=negative_prompt,
        args=args,
        out_dir=out_dir
    )

    for _ in tqdm(animator.render(), total=args.max_frames):
        pass

    create_video_from_frames(
        animator.out_dir, f"{video_output_filename}.mp4", fps=24)
