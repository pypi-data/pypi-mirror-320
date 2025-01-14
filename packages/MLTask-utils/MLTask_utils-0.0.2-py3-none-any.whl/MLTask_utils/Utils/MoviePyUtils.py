from random import randint
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy import TextClip, concatenate_videoclips, VideoFileClip
# from moviepy.video.tools.segmenting import findObjects
from moviepy.video.VideoClip import write_gif
import time
import numpy as np
import os


def shake(t, pos):
    speed = 5
    d = randint(0, 4)
    if 0 == d:  # top
        return (pos[0], pos[1] + speed)
    elif 1 == d:  # left
        return (pos[0] - speed, pos[1])
    elif 2 == d:  # bot
        return (pos[0], pos[1] - speed)
    else:  # right
        return (pos[0] + speed, pos[1])


def rotMatrix(a): return np.array([[np.cos(a), np.sin(a)],
                                   [-np.sin(a), np.cos(a)]])


def vortex(screenpos, i, nletters):
    def d(t): return 1.0 / (0.3 + t**8)  # damping
    a = i * np.pi / nletters  # angle of the movement
    v = rotMatrix(a).dot([-1, 0])
    if i % 2:
        v[1] = -v[1]
    return lambda t: screenpos + 400 * d(t) * rotMatrix(0.5 * d(t) * a).dot(v)


def cascade(screenpos, i, nletters):
    v = np.array([0, -1])
    def d(t): return 1 if t < 0 else abs(np.sinc(t) / (1 + t**4))
    return lambda t: screenpos + v * 400 * d(t - 0.15 * i)


def arrive(screenpos, i, nletters):
    v = np.array([-1, 0])
    def d(t): return max(0, 3 - 3 * t)
    return lambda t: screenpos - 400 * v * d(t - 0.2 * i)


def vortexout(screenpos, i, nletters):
    def d(t): return max(0, t)  # damping
    a = i * np.pi / nletters  # angle of the movement
    v = rotMatrix(a).dot([-1, 0])
    if i % 2:
        v[1] = -v[1]
    return lambda t: screenpos + 400 * d(t - 0.1 * i) * rotMatrix(-0.2 * d(t) * a).dot(v)


# WE USE THE PLUGIN findObjects TO LOCATE AND SEPARATE EACH LETTER


# WE ANIMATE THE LETTERS

def moveLetters(letters, funcpos):
    return [letter.set_pos(funcpos(letter.screenpos, i, len(letters)))
            for i, letter in enumerate(letters)]


# https://zulko.github.io/moviepy/examples/moving_letters.html
def get_text_animation_clip(text, screensize, duration=1, color='white', bg_color="transparent", font="Amiri-Bold", fontsize=100, fps=25, out_directory_path="out"):
    txtClip = TextClip(txt=text, color=color, font=font,
                       kerning=5, fontsize=fontsize, bg_color=bg_color).set_duration(duration)
    cvc = CompositeVideoClip([txtClip.set_pos('center')], size=screensize)
    # letters = findObjects(cvc)

    # if not letters:
    #     print("No letters")
    #     return cvc
    # # vortex, cascade, arrive, vortexout
    # letter_clips = moveLetters(letters, cascade)
    # composite_clips = CompositeVideoClip(
    #     letter_clips, size=screensize).set_start(0).set_duration(duration)

    # unix_timestamp = int(time.time())
    # final_output_video_filepath = os.path.join(
    #     out_directory_path, f'letter-video-{unix_timestamp}.mp4')
    # composite_clips.write_videofile(final_output_video_filepath, fps=fps)
    # return final_output_video_filepath
    # clips = [CompositeVideoClip(moveLetters(letters, funcpos), size=screensize).subclip(0, 5)
    #          for funcpos in [vortex, cascade, arrive, vortexout]]
    # return concatenate_videoclips(clips)
