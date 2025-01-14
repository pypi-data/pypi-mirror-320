import os
from tqdm import tqdm
import random
import time
from moviepy import ColorClip, ImageClip, vfx, CompositeVideoClip, AudioFileClip, TextClip, concatenate_videoclips, concatenate_audioclips


class Img2Lookbook:

    def __init__(self, width, height, duration, fit, zoom_factor, transition_duration=0.5):

        self.output_width = width
        self.output_height = height
        self.duration = duration
        self.fit = fit
        self.zoom_factor = zoom_factor
        self.transition_duration = transition_duration
        self.fps = 30

    @staticmethod
    def is_image_file(file_path):
        _, file_extension = os.path.splitext(file_path)
        # Add other image file extensions as needed
        text_extensions = ['.jpg', '.png', '.jpeg', '.webp']
        return file_extension.lower() in text_extensions

    @staticmethod
    def is_sound_file(file_path):
        _, file_extension = os.path.splitext(file_path)
        # Add other image file extensions as needed
        text_extensions = ['.wav', '.mp3']
        return file_extension.lower() in text_extensions

    def make(self, in_file):

        # bg
        clip_bg = ColorClip(
            size=(self.output_width, self.output_height), color=[0, 0, 0])
        clip_bg = clip_bg.set_duration(self.duration).set_fps(self.fps)

        # image
        clip_fg = ImageClip(in_file)

        clip_fg = (clip_fg.fx(vfx.resize, height=self.output_height))
        if self.fit == "width":
            clip_fg = (clip_fg.fx(vfx.resize, width=self.output_width))

        clip_fg = clip_fg.set_duration(self.duration).set_fps(self.fps)
        clip_fg_init_size = clip_fg.size

        # scale up for zooming effect
        clip_effect = (clip_fg.fx(vfx.resize, 1.5))

        # white block
        clip_white = None
        try:
            clip_white = ColorClip(size=(
                (self.output_width - clip_fg.size[0]) // 2, self.output_height), color=[0, 0, 0])
            if self.fit == "width":
                clip_white = ColorClip(size=(
                    self.output_width, (self.output_height - clip_fg.size[1]) // 2), color=[0, 0, 0])

            clip_white = clip_white.set_duration(
                self.duration).set_fps(self.fps)

        except Exception as ex:
            print(str(ex))
            clip_white = None

        start_scale = 1
        end_scale = self.zoom_factor

        def scale_up_func(t):
            current_scale = start_scale + \
                (end_scale - start_scale) * (t / self.duration)
            return current_scale / 1.5

        txt_clip = TextClip("CUTE", fontsize=70, color="red",
                            bg_color="transparent", size=(self.output_width - 10, 60))

        text_duration_offset = 0.3

        # x_pos_rand = random.randint(0, self.output_width)
        x_pos_rand = 0
        y_pos_rand = random.randint(
            self.output_height / 4, self.output_height * 3 / 4)
        txt_clip = txt_clip.set_position((x_pos_rand, y_pos_rand)).set_duration(
            (self.duration - text_duration_offset) / 8)
        txt_clip = txt_clip.set_start(text_duration_offset * 2)

        sticker_size = 300
        sticker_clip = ImageClip('Social/youtube/sticker.png')
        # image = image.set_position(("center", "top"))  # Adjust position as needed

        x_pos_rand = random.randint(
            self.output_width / 4, self.output_width * 3 / 4)
        y_pos_rand = random.randint(
            self.output_height / 4, self.output_height * 3 / 4)
        sticker_clip = sticker_clip.set_position(
            (x_pos_rand, y_pos_rand)).set_duration(
            (self.duration - text_duration_offset) / 5).resize(
            # Adjust position as needed
            (sticker_size, sticker_size)).rotate(random.randint(-45, 45)).set_start(text_duration_offset)

        video_zoom_in = CompositeVideoClip([
            clip_bg,
            clip_effect.fx(vfx.resize, scale_up_func).set_position(
                lambda t: ('center', 'center')),
            # txt_clip,
            # sticker_clip

        ])

        # if clip_white:
        #     video_zoom_in = CompositeVideoClip([
        #         clip_bg,

        #         clip_effect.fx(vfx.resize, scale_up_func).set_position(
        #             lambda t: ('center', 'center')),
        #         clip_white.set_position((0, 0)),
        #         clip_white.set_position(
        #             (clip_white.size[0] + clip_fg_init_size[0], 0)),
        #         txt_clip,
        #     ])

        #     if self.fit == "width":
        #         video_zoom_in = CompositeVideoClip([
        #             clip_bg,
        #             clip_effect.fx(vfx.resize, scale_up_func).set_position(
        #                 lambda t: ('center', 'center')),
        #             clip_white.set_position((0, 0)),
        #             clip_white.set_position(
        #                 (0, clip_white.size[1] + clip_fg_init_size[1])),
        #             txt_clip,
        #         ])

        if self.transition_duration > 0:
            video_zoom_in = video_zoom_in.fx(
                vfx.fadein, self.transition_duration / 2).fx(
                vfx.fadeout, self.transition_duration / 4)

        return video_zoom_in

    def batch_make_and_save(self, in_directory_path, music_bg_directory_path, out_directory_path):

        # Get a list of all files in the directory
        files = [f for f in os.listdir(in_directory_path) if os.path.isfile(
            os.path.join(in_directory_path, f))]

        files = list(filter(
            lambda string: 'thumbnail' not in string and '.DS_Store' not in string, files))

        files.sort()

        # Check if the directory already exists
        if not os.path.exists(out_directory_path):
            # If it does not exist, create it
            os.makedirs(out_directory_path)

        clip_videos = []

        # Loop through the operation and update the progress bar
        operation_length = len(files)
        if operation_length == 0:
            # Raise an Error with a custom error message
            raise Exception(
                "Error processing video: no images found in source images directory!")
        print("----------------")
        with tqdm(total=operation_length) as pbar:

            # Add token to an input file at path in_file and save the result to out_file
            for i, file in enumerate(files):
                file_name, file_extension = os.path.splitext(file)

                in_file = os.path.join(in_directory_path, file)

                print(f'makeing video for image {file}')
                try:
                    if self.is_image_file(in_file):
                        clip_video = self.make(in_file)
                        clip_videos.append(clip_video)

                except Exception as ex:
                    print(str(ex))

                # Update the progress bar
                pbar.update(1)

        # Join videos

        # Videos
        videos_concat_clip = concatenate_videoclips(clip_videos)

        # Final
        final_video_clips = [videos_concat_clip]

        # Music background
        if music_bg_directory_path.strip() != '':
            music_bgs = [f for f in os.listdir(music_bg_directory_path) if os.path.isfile(
                os.path.join(music_bg_directory_path, f))]

            music_bgs = [f for f in music_bgs if self.is_sound_file(f)]
            print('music_bgs = ')
            print(music_bgs)
            if len(music_bgs) > 0:
                music_bg = random.sample(music_bgs, 1)[0]
                print(f'using bg music {music_bg}')

                bg_music_clip = AudioFileClip(
                    os.path.join(music_bg_directory_path, music_bg))
                num_bg_music_repeat = int(
                    videos_concat_clip.duration // bg_music_clip.duration) + 1
                cc_bg_music_clip = concatenate_audioclips(
                    [bg_music_clip for _ in range(num_bg_music_repeat)]).set_duration(videos_concat_clip.duration)

                # Final
                print('cc_bg_music_clip =')
                print(cc_bg_music_clip)
                videos_concat_clip = videos_concat_clip.set_audio(
                    cc_bg_music_clip)
                final_video_clips = [videos_concat_clip]

        # Final
        final_video_clip = CompositeVideoClip(final_video_clips)
        if len(final_video_clips) == 1:
            final_video_clip = final_video_clips[0]

        unix_timestamp = int(time.time())
        final_output_video_filepath = os.path.join(
            out_directory_path, f'video-{unix_timestamp}.mp4')
        final_video_clip.write_videofile(
            final_output_video_filepath, fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True)

        return final_output_video_filepath
