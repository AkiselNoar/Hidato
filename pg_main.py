#!/usr/bin/python3
# -*- coding: utf-8 -*-

from random import randint, choice, shuffle
from itertools import cycle
from time import time
from math import *

import pygame as pg
import pygame.locals as pgl

pg.init()

BG = (25, 10, 35)
FG = (220, 245, 210)
DIMFG = (70, 95, 50)


class Cell:
    SIZE = 30
    PATHWAY = ((2, 1), (1, 2), (0, 1), (1, 0))
    DNAME = "ESWN"
    COLOR_GRID = DIMFG
    PATH_COLOR = FG
    COLOR_MARK = (150, 80, 105)
    
    def __init__(self, pos):
        self.pos = pos
        self.way = [0, 0, 0, 0]  #E, S, W, N
        self._marked = False
        self.done = False

    def mark(self):
        self._marked = True

    def unmark(self):
        self._marked = False

    def set_way(self, d):
        if d in self.DNAME:
            d = self.DNAME.index(d)
        self.way[d] = not self.way[d]

    @property
    def marked(self):
        return any(self.way)

    def draw(self, screen, pos):
        x, y = pos
        if any(self.way) or self._marked:
            color = self.PATH_COLOR
            if self._marked:
                color = self.COLOR_MARK
            pg.draw.rect(screen, color, (x+self.SIZE/3, y+self.SIZE/3, self.SIZE/3, self.SIZE/3))
            for (modx, mody), p in zip(self.PATHWAY, self.way):
                if p:
                    pg.draw.rect(screen, self.PATH_COLOR, (x+modx*self.SIZE/3, y+mody*self.SIZE/3, self.SIZE/3, self.SIZE/3))


        #pg.draw.rect(screen, self.COLOR_GRID, (x, y, self.SIZE, self.SIZE), 1)

class Grid:
    def __init__(self, width, height):
        self.grid = list()
        for x in range(width):
            l = list()
            self.grid.append(l)
            for y in range(height):
                l.append(Cell((x, y)))

    def get_width(self):
        return len(self.grid)

    def get_height(self):
        return len(self.grid[0])

    def draw(self, screen, pos=(0, 0)):
        for x, l in enumerate(self.grid):
            for y, c in enumerate(l):
                cx = pos[0] + Cell.SIZE * x
                cy = pos[1] + Cell.SIZE * y
                c.draw(screen, (cx, cy))

    def get_cell(self, x, y):
        return self.grid[x][y]

    def get_neighbour(self, pos, d):
        x, y = pos
        match d:
            case "S": y = (y + 1 + self.get_height()) % self.get_height()
            case "N": y = (y - 1 + self.get_height()) % self.get_height()
            case "E": x = (x + 1 + self.get_width()) % self.get_width()
            case "W": x = (x - 1 + self.get_width()) % self.get_width()
        return self.get_cell(x, y)
        if d == "S" and y+1<self.get_height():
            y += 1
        elif d == "N" and y-1>=0:
            y -= 1
        elif d == "W" and x-1>=0:
            x -= 1
        elif d == "E" and x+1<self.get_width():
            x += 1
        else:
            raise IndexError
        return self.get_cell(x, y)

class Player:
    def __init__(self, grid, pos, color_path=FG, inv=False):
        self.grid = grid
        self.pos = pos
        self.history = list()
        self.color_path = color_path
        self.inv = inv

    def move(self, d):
        if not self.move_available(d):
            return False
        if self.inv:
            d = Cell.DNAME[Cell.DNAME.index(d)-2]
        orig = self.grid.get_cell(*self.pos)
        dest = self.grid.get_neighbour(self.pos, d)
        orig.PATH_COLOR = self.color_path
        dest.PATH_COLOR = self.color_path
        orig.unmark()
        dest.mark()
        orig.set_way(d)
        dest.set_way(Cell.DNAME[Cell.DNAME.index(d)-2])
        self.history.append(self.pos)
        self.pos = dest.pos
        return True

    def move_available(self, d):
        if self.inv:
            d = Cell.DNAME[Cell.DNAME.index(d)-2]
        r = True
        try:
            dest = self.grid.get_neighbour(self.pos, d)
        except IndexError:
            r = False
        else:
            if dest.marked:
                r = False
        return r

    def get_cell(self):
        return self.grid.get_cell(*self.pos)

    def rewind(self):
        self.grid.get_cell(*self.pos).unmark()
        self.pos = self.history.pop()
        self.grid.get_cell(*self.pos).mark()


def main():

    px_size = 1600, 1000
    Cell.SIZE = 15
    Cell.PATHWAY = ((2, 2), (0, 2), (0, 0), (2, 0))
    grid_size = tuple(s//Cell.SIZE for s in px_size)
    grid_size_px = [s*Cell.SIZE for s in grid_size]
    offset_px = [a-b for a, b in zip(px_size, grid_size_px)]
    display = pg.display.set_mode(px_size)
    surf = pg.Surface(grid_size_px)
    display.fill(BG)
    surf.fill(BG)
    print(offset_px)
    print(surf.get_size())
    clock = pg.time.Clock()

    grid = Grid(*grid_size)

    colors = cycle(((95, 75, 100), (45, 35, 70), (55, 55, 85)))
    players = list()

    nb = 6
    cx, cy = [v//2 for v in grid_size]
    players = [Player(grid, (cx, cy))]


    """
    from Anana import going_round
    radius = grid_size[0]//3
    for i, pts in zip(range(nb), going_round(nb, (cx, cy), radius)):
        players.append(Player(grid, pts,
                              next(colors),
                              i%2
                              ))
        print(players[-1].pos)
    """


    """
    j = 0
    for j in [(15, True), (-15, False),((grid_size[0]//2)+15, True), ((grid_size[0]//2)-15, False)]:#range(0, grid_size[0], 25):
        j, inv = j
        for i in range(0, grid_size[1], grid_size[1]//6):
            next(colors)
            pos = [j,# + 5*(i%3),
                i + 5*inv
                    ]
            #pos = [randint(0, g-1) for g in grid_size]
            try:
                grid.get_cell(*pos).mark()
            except IndexError:
                continue
            players.append(Player(grid, pos, next(colors), inv))
    """

    def move(d):
        for p in players:
            p.move(d)

    loop = True
    pause = not True
    counter = cycle(range(1))
    while loop:
        for e in pg.event.get():
            if e.type == pgl.QUIT:
                loop = False
            if e.type == pgl.KEYDOWN:
                match e.key:
                    case pgl.K_SPACE:
                        pause = not pause
                    case pgl.K_s:
                        name = f"ss_{time()}.jpg"
                        print("saved", name)
                        pg.image.save(surf, name)
        if not pause:# and not next(counter):
            ds = list("SNEW")
            shuffle(ds)
            moved = False
            if not any(player.get_cell().done for player in players):
                for d in ds:
                    if all(player.move_available(d) for player in players):
                        moved = True
                        r = 3
                        for _ in range(r):
                            for player in players:
                                player.move(d)
            if not moved:
                for player in players:
                    player.get_cell().done = True
                    try:
                        player.rewind()
                    except IndexError:
                        print("pause")
                        pause = True
                        for player in players:
                            player.get_cell().unmark()
                        break
        surf.fill(BG)
        grid.draw(surf)
        display.blit(surf, offset_px)
        pg.display.update()
        clock.tick(30)

if __name__ == "__main__":
    main()
