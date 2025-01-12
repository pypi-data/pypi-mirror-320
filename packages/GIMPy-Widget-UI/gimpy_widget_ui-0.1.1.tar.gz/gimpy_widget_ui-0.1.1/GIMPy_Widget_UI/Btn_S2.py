import re
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from enum import Enum


class Draw_Over_Under(Enum):
    OVER = True
    UNDER = False

class Btn_S2:
    def __init__(self, btnName, canvas, base_image_size, polygon, base_image, color_selected=(79, 18, 9, 180),
                 drawmode=Draw_Over_Under.OVER, command=None):
        self.__tk_image = None
        self.__command = command
        self.__base_image = base_image
        self.__canvas = canvas
        self.__base_image_size = base_image_size
        self.__color_selected = color_selected
        self.__btnName = btnName
        self.__drawmode = drawmode
        self.__polygon = polygon
        self.__selected_Btn = None
        self.__draw_polygon()
        self.__saved_image = None


    def __add_remove_skin(self, status: bool):
        trans_image = Image.new('RGBA', self.__base_image_size, (255, 255, 255, 0))
        fill_color = None

        # Select color to be filled in the polygon when its created based on Valid click event
        if status:
            fill_color = self.__color_selected
        else:
            fill_color = (0, 0, 0, 0)

        def draw_polygon(fill_color):
            draw = ImageDraw.Draw(trans_image, "RGBA")
            draw.polygon(self.__polygon, fill_color)

        draw_polygon(fill_color=fill_color)

        if self.__drawmode == Draw_Over_Under.OVER:
            self.__saved_image = Image.alpha_composite(self.__base_image, trans_image)

        if self.__drawmode == Draw_Over_Under.UNDER:
            self.__saved_image = Image.alpha_composite(trans_image, self.__base_image)

        combined_image = self.__saved_image

        self.__tk_image = ImageTk.PhotoImage(combined_image)
        self.__canvas.itemconfig('baseImage', image=self.__tk_image)
        del combined_image
        del trans_image

    def __draw_polygon(self):
        tag = self.__btnName
        self.__canvas.create_polygon(self.__polygon, fill='', outline='', tags=tag, width=0)
        self.__canvas.tag_bind(tag, '<ButtonPress>', self.__top_layer_mouse_dn)
        self.__canvas.tag_bind(tag, '<B1-Motion>', self.__top_layer_mouse_drag)
        self.__canvas.tag_bind(tag, '<ButtonRelease>', self.__top_layer_mouse_up)


    def __top_layer_mouse_dn(self, event):
        x, y = event.x, event.y
        closesttag = self.__canvas.find_closest(event.x, event.y)
        tag_name = self.__canvas.gettags(closesttag)
        self.__add_remove_skin(True)


    def __top_layer_mouse_drag(self, event):
        x, y = event.x, event.y
        closesttag = self.__canvas.find_closest(event.x, event.y)
        tag_name = self.__canvas.gettags(closesttag)

        if tag_name[0] == self.__btnName:
            self.__add_remove_skin(True)
        else:
            self.__add_remove_skin(False)

    def __top_layer_mouse_up(self, event):
        self.__add_remove_skin(False)
        x, y = event.x, event.y
        closesttag = self.__canvas.find_closest(event.x, event.y)
        tag_name = self.__canvas.gettags(closesttag)
        self.__add_remove_skin(False)

        if self.__command is not None and tag_name[0] == self.__btnName:
            self.__command(tag_name[0])


    @staticmethod
    def str_to_coordinates(file_loc, control_name, parameter_offset):
        coordinates = None
        with open(file_loc, 'r') as file:
            lines = file.readlines()

        for line in lines:
            split_params = line.split(":")
            if split_params[1] == control_name:
                match = re.findall(r'\((\d+),\s*(\d+)\)', split_params[parameter_offset - 1].strip())
                coordinates = [tuple(map(int, coord)) for coord in match]
                break

        if coordinates is None:
            raise ValueError(f"Control Name={control_name} not found in {file_loc}")

        return coordinates
