import pygame
import pygame.gfxdraw
import random
import struct
from pydub import AudioSegment
import math
import sys

FRAME_RATE = 50

track = AudioSegment.from_file(sys.argv[1])
left_track, right_track = track.split_to_mono()

pygame.mixer.pre_init(frequency=track.frame_rate, size=-16, channels=2, buffer=256)
pygame.init()

screen = pygame.display.set_mode((500, 500))

clock = pygame.time.Clock()


class GraphDisplay:
    def __init__(self):
        self._s = None
        self._cursor = (
            round(screen.get_size()[0] / 2),
            round(screen.get_size()[1] / 2),
        )
        self.reset()

    def reset(self):
        self._s = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)

    def plot(self, x: float, y: float) -> None:
        x = round(x)
        y = round(y)

        c_x, c_y = self._cursor

        d_x = x - c_x
        d_y = y - c_y

        distance = math.sqrt(d_x ** 2 + d_y ** 2)

        if distance < 50:
            pygame.draw.line(self._s, (0, 255, 0), (c_x, c_y), (x, y))
        else:
            pygame.gfxdraw.pixel(self._s, x, y, pygame.Color("green"))

        self._cursor = (x, y)

    def get_surface(self):
        return self._s


def buf_to_val(b_str: bytes):
    return struct.unpack("h", b_str)[0]


def calc_axis_pos(frame_val: float, max_val: float, axis_res: int):
    delta = (frame_val / max_val) * (axis_res / 2)
    return axis_res / 2 - delta


display = GraphDisplay()

sound_frame_num = 0

try:
    finished = False

    while not finished:
        display.reset()

        audio_frames = b""

        for i in range(int(track.frame_rate / FRAME_RATE)):
            audio_frames += track.get_frame(sound_frame_num)

            l_frame_val = buf_to_val(left_track.get_frame(sound_frame_num))
            r_frame_val = buf_to_val(right_track.get_frame(sound_frame_num))

            x_res, y_res = screen.get_size()

            x, y = (
                calc_axis_pos(l_frame_val, track.max_possible_amplitude, x_res),
                calc_axis_pos(r_frame_val, track.max_possible_amplitude, y_res),
            )

            display.plot(x, y)

            sound_frame_num += 1

        # Make the screen black
        screen.fill((0, 0, 0))
        screen.blit(display.get_surface(), (0, 0))

        # Handle close buttons
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                finished = True
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.unicode == "q":
                    finished = True
                    break

        pygame.display.flip()

        clock.tick(FRAME_RATE)
        pygame.mixer.Sound(buffer=audio_frames).play()
finally:
    pygame.quit()
