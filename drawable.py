import os
import random
from typing import Tuple

from PIL import Image, ImageFont, ImageFilter
from PIL import ImageDraw


def isIn(posX: int, posY: int, x: int, y: int, x1: int, y1: int, expand: int = 0):
    x = x - expand
    y = y - expand
    x1 = x1 + expand
    y1 = y1 + expand

    return x < posX < x1 and y < posY < y1

class Snow:
    def __init__(self, xy: tuple[int, int], radius: int, fill: str, screen_xy: tuple[int, int], max_frames: int):
        self.__xy = xy
        self.__radius = radius
        self.__fill = fill
        self.__screen_xy = screen_xy
        self.__step = 0
        self.__max_frames = max_frames
        self.__opacity = random.randint(20, 100) / 100.0
        self.__moves = []

        for i in range(max_frames):
            self.__moves.append([
                -.3,
                1
            ])

    def _get_random_xy(self) -> Tuple[int, int]:
        return random.randint(-5, self.__screen_xy[0] + 5), random.randint(-5, self.__screen_xy[1] + 5)

    def move(self):
        move = self.__moves[self.__step]

        self.__xy = (self.__xy[0] + move[0], self.__xy[1] + move[1])

        if self.__xy[1] > self.__screen_xy[1] + 5:
            self.__xy = (self.__xy[0], -5)

        if self.__xy[0] < -5:
            self.__xy = (self.__screen_xy[0] + 5, self.__xy[1])

        self.__step += 1

    def draw(self, draw: ImageDraw):
        if self.__radius <= 0:
            return

        draw.ellipse((
            self.__xy[0] - self.__radius,
            self.__xy[1] - self.__radius,
            self.__xy[0] + self.__radius,
            self.__xy[1] + self.__radius),
            fill=(255, 255, 255, int(self.__opacity * 255)))

class Snows:
    def __init__(self, screen_xy: Tuple[int, int], max_frames: int, deadzone: Tuple[int, int, int, int], expand: int = 0):
        self.__particles = []
        self.__screen_xy = screen_xy
        self.__max_frames = max_frames
        self.__deadzone = deadzone
        self.__expand = expand

    def _get_random_xy(self) -> Tuple[int, int]:
        return random.randint(-5, self.__screen_xy[0] + 5), random.randint(-5, self.__screen_xy[1] + 5)

    def generate(self, p_min: int, p_max: int, fill: str):
        for i in range(random.randint(p_min, p_max)):
            center = self._get_random_xy()

            if isIn(center[0], center[1], self.__deadzone[0], self.__deadzone[1], self.__deadzone[2], self.__deadzone[3], self.__expand):
                continue

            radius = random.randint(2, 6)
            self.__particles.append(Snow(center, radius, fill, self.__screen_xy, self.__max_frames))

    def draw(self, draw: ImageDraw):
        for particle in self.__particles:
            particle.draw(draw)

    def move(self):
        for particle in self.__particles:
            particle.move()

class Drawable:
    def __init__(self, qr: Image):
        self.__qr: Image = qr
        self.__image: Image = Image.new('RGB', (300, 600), color="#302f2b")
        self.__font_18: ImageFont = ImageFont.truetype("assets/Nunito-Regular.ttf", 18)
        self.__font_16: ImageFont = ImageFont.truetype("assets/Nunito-Regular.ttf", 16)
        self.__font_14: ImageFont = ImageFont.truetype("assets/Nunito-Regular.ttf", 14)
        self.__font_12: ImageFont = ImageFont.truetype("assets/Nunito-Regular.ttf", 12)
        self.__draw: ImageDraw = ImageDraw.Draw(self.__image, 'RGBA')
        self.__size: Tuple[int, int] = self.__image.size

        self.drawSnow()
        self.drawQR()
        self.drawText()

        self.__image.save("save.png")

    def drawTriangle(self, vertices: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]], *args, **kwargs) -> None:
        self.__draw.polygon(vertices, *args, **kwargs)

    def drawSnow(self):
        snow_img = Image.new('RGB', (300, 245), color="#302f2b")
        snow_draw = ImageDraw.Draw(snow_img, "RGBA")

        snows: Snows = Snows((300, 230), 1, (65, 30, 235, 200), 10)
        snows.generate(150, 200, "white")

        snows.move()
        snows.draw(snow_draw)

        snow_img = snow_img.filter(ImageFilter.GaussianBlur(radius=2))

        self.__image.paste(snow_img, (0, 0))

    def drawQR(self):
        self.__qr = self.__qr.convert("RGBA").resize((170, 170))

        mask = Image.new('L', self.__qr.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, 170, 170), radius=6, fill=255)

        logo = Image.open("assets/logo.png").convert("RGBA").resize((50, 50))
        position = ((self.__qr.width - logo.width) // 2, (self.__qr.height - logo.height) // 2)
        self.__qr.paste(logo, position, mask=logo)

        self.__image.paste(
            self.__qr, ((300 - self.__qr.width) // 2, (230 - self.__qr.height) // 2), mask=mask
        )

    def drawNickname(self):
        nick_img = Image.new('RGBA', (370*2, 370*2), color="#1c1b19")
        nick_draw = ImageDraw.Draw(nick_img, 'RGBA')

        width, height = nick_draw.textlength(".1qxz", font=self.__font_12)+4, 16
        Hstep = 0
        Wstep = 0

        while Wstep * width < nick_img.width:
            while Hstep * height < nick_img.height:
                nick_draw.text((Wstep*width, Hstep*height), ".1qxz", font=self.__font_12, fill="#1d1d1a")
                Hstep+=1

            Hstep=0
            Wstep+=1

        nick_mask = Image.new('L', nick_img.size, 0)
        mask_draw = ImageDraw.Draw(nick_mask)
        mask_draw.rectangle((0, 230, self.__size[0]+nick_img.width//2, self.__size[1]), fill=255)

        mask_draw.polygon(((127+nick_img.width//2-10, 232), (150+nick_img.width//2-10, 207), (185+nick_img.width//2-10, 245)), fill=255)

        nick_img = nick_img.rotate(45)

        self.__image.paste(nick_img, (-nick_img.width//2+10, 0), mask=nick_mask)

    def drawTextBackground(self):
        self.drawTriangle(((127, 232), (150, 207), (185, 245)), fill="#1c1b194d")

        self.__draw.rectangle((0, 226, self.__size[0], 235), fill="#1c1b194d")  # background
        self.__draw.rectangle((0, 230, self.__size[0], self.__size[1]), fill="#1c1b19") # background
        self.drawTriangle(((120, 245), (150, 215), (180, 245)), fill="#1c1b19")

        vertices = [
            ((self.__size[0] - 30 - 5, self.__size[1] - 5), (self.__size[0] - 5, self.__size[1] - 30 - 5), (self.__size[0] - 5, self.__size[1] - 5))
        ]

        for ver in vertices:
            self.drawTriangle(ver, fill="#21201f")

        self.drawNickname()

    def drawText(self):
        self.drawTextBackground()

        self.__draw.text(
            (16, 245), "To pass the verification, you\nneed to follow a couple of steps.", "white",
            self.__font_18)

        self._drawStep(318-5, 1, "Open Discord on your phone.")
        self._drawStep(344-5, 2, "Go to the settings.")
        self._drawStep(370-5, 3, "In the settings,\nclick on \"Scan QR Code\".")
        self._drawStep(415-5, 4, "Scan the QR code you see above.")
        self._drawStep(441-5, 5, "After scanning,\nclick on the blue button.")

        self.__draw.text(
            (16, 500),
            "If you followed all the steps,\n" +
            "congratulations! You have passed the\n" +
            "bot check and can access this\n" +
            "Discord server.", "white",
            self.__font_16)

    def _drawStep(self, y: int, step: int, text: str) -> None:
        self.__draw.text(
            (16, y), f"{step}.", "#b3b3b3",
            self.__font_14)

        self.__draw.text(
            (39, y), text, "white",
            self.__font_14)
