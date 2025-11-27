from PIL import Image
import os

PATH = (255, 255, 255)
WALL = (0, 0, 0)
VISITED = (0, 0, 255)
WALKED = (255, 0, 0)


class MazeImage:
    def __init__(self, p):
        self._path = os.path.abspath(p)
        self._im = Image.open(self._path)
        self._im.convert("RGB")
        # print(self._path)

    def getwidth(self) -> int:
        w, h = self._im.size
        return w

    def getheight(self) -> int:
        w, h = self._im.size
        return h

    def getpixel(self, x: int, y: int) -> int:
        p = self._im.getpixel((x, y))
        return p

    def is_wall(self, x: int, y: int) -> bool:
        p = self.getpixel(x, y)
        return p == WALL

    def is_path(self, x: int, y: int) -> bool:
        p = self.getpixel(x, y)
        return p == PATH

    def is_visited(self, x: int, y: int) -> bool:
        p = self.getpixel(x, y)
        return p == VISITED

    def show(self):
        self._im.show()

    def set_visited(self, x: int, y: int):
        self._im.paste(VISITED, (x, y, x + 1, y + 1))

    def set_walked(self, x: int, y: int):
        self._im.paste(WALKED, (x, y, x + 1, y + 1))

    def putpixel(self, x: int, y: int, color: tuple):
        self._im.paste(color, (x, y, x + 1, y + 1))

    def save_image(self):
        self._im.save(os.path.abspath("mymaze.png"))

    def filter_grayscale(self):
        for y in range(self.getheight()):
            for x in range(self.getwidth()):
                color = self._im.getpixel((x, y))
                gray = int((color[0] + color[1] + color[2]) / 3)
                self.putpixel(x, y, (gray, gray, gray))


imo = MazeImage("rooster.png")
imo.filter_grayscale()
imo.save_image()