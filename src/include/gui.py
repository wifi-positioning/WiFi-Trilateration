#!/usr/bin/env python3
from tkinter import *
from PIL import Image, ImageTk

class Window(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.initUI()

    def initUI(self):
        self.master.title("WiFi Positioning")
        self.pack(fill=BOTH, expand=1)
        self.map = ImageTk.PhotoImage(Image.open("data/images/map_modded.png"))
        self.layer = Canvas(self, width=1200, height=1023)
        self.layer.create_image(0, 0, anchor=NW, image=self.map)
        self.layer.pack(fill=BOTH, expand=1)

    def drawPos(self, position_list):
        self.agent = ImageTk.PhotoImage(Image.open("data/images/agent.png"))
        for position in position_list:
            if position:
                posX = position[0]
                posY = position[1]

                # pixelX = Top left angle of the blue box on map + N Square * Grid Multiply - Half of the phone's img size
                # pixelY = Top left angle of the blue box on map + N Square * Grid Multiply - Half of the phone's img size
                pixelX = 291 + posX * 30.1 - 8
                pixelY = 22 + posY * 30.1 - 13

                self.layer.create_image(pixelX, pixelY, anchor=NW, image=self.agent)
                self.layer.create_text(pixelX+4, pixelY+7, anchor=NW, text=position_list.index(position)+1)
                self.layer.pack(fill=BOTH, expand=1)
