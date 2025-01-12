import tkinter as tk
from enum import Enum
import re
from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np


class Draw_Over_Under(Enum):
    OVER = True
    UNDER = False


class RadioClassS2:
    def __init__(self, radioBtnName: str, canvas, polygon: list, imageLayers: dict, drawmode=Draw_Over_Under.OVER,
                 color_selected=(2, 255, 255, 180), default=False, command=None):
        self.__canvas = canvas
        self.__btnName = radioBtnName
        self.__drawmode = drawmode
        self.__color_selected = color_selected
        self.__command = command
        self.__imageLayers = imageLayers
        # imagelayers dictionary items consists of a list of images. Base image + an initially blank saved image
        __radio_grp_name = str(radioBtnName).split('*')[0]
        self.__base_image, self.__savedimage = self.__imageLayers["Radio_Style1*" + __radio_grp_name]

        self.__polygon = polygon
        self.__draw_polygon()
        self.__tk_image = None

        self.__last_value = None
        # This will select the default radio button without the user selecting it
        if not default:
            self.__change_radio_Status(radioBtnName, False)
            self.__last_value = False
        else:
            # print(f'{radioBtnName} is set as Default')
            self.__change_radio_Status(radioBtnName, True)
            self.__last_value = True

        self.__selected_points = None
        self.__bring_polygons_to_top()

    def __bring_polygons_to_top(self):
        # Find all items on the canvas
        items = self.__canvas.find_all()
        # Iterate through the items and bring polygons to the top
        for item in items:
            if self.__canvas.type(item) == 'polygon':
                self.__canvas.tag_raise(item)

    def __findallchildren(self):
        items = self.__canvas.find_all()
        print(f"{len(items)} items found...")

        for item in items:
            print(f"Item ID: {item}, Type: {self.__canvas.type(item)}")
            item_tags = self.__canvas.gettags(item)
            item_name = item_tags[0] if item_tags else "No name"
            print(f"Item ID: {item}, Name: {item_name}")

    def __load_image(self):
        # Load the image using PIL
        self.__tk_image = ImageTk.PhotoImage(self.pil_image)
        self.__canvas.create_image(0, 0, anchor=tk.NW, image=self.__tk_image, tags=self.__btnName + "TempRadioImage")

    def __draw_polygon(self):
        tag = self.__btnName
        self.__canvas.create_polygon(self.__polygon, fill='', outline='', tags=tag, width=0)
        self.__canvas.tag_bind(tag, '<ButtonPress>', self.__radio_top_layer_mouse_dn)
        self.__canvas.tag_bind(tag, '<ButtonRelease>', self.__radio_top_layer_mouse_up)

    def __radio_top_layer_mouse_dn(self, event):
        x, y = event.x, event.y

        if self.__is_point_in_polygon(x, y, self.__polygon):
            closesttag = self.__canvas.find_closest(event.x, event.y)
            tag_name = self.__canvas.gettags(closesttag)
            self.selected_Btn = tag_name[0]
            self.__selected_points = self.__polygon

    def __radio_top_layer_mouse_up(self, event):
        x, y = event.x, event.y
        closesttag = self.__canvas.find_closest(event.x, event.y)
        tag_name = self.__canvas.gettags(closesttag)

        # if tuple tag_name is empty that means the mouse was released outside the button area
        if len(tag_name) and self.selected_Btn == tag_name[0]:
            self.__change_radio_Status(self.selected_Btn, True)

            if self.__command is not None:
                self.__command(self.selected_Btn)
                # Placeholder to call function that handles button press

        else:
            self.selected_Btn = None

        # self.findallchildren()

    def __is_point_in_polygon(self, x, y, points):
        # Convert points to a format suitable for cv2.pointPolygonTest
        contour = np.array(points, dtype=np.int32)
        return cv2.pointPolygonTest(contour, (x, y), False) >= 0

    def __change_radio_Status(self, selected_btn, Status):
        # Pass selected_btn as argument to this function so that the function can also be called
        # for a default button when creating an instance for a radio.
        trans_image = Image.new('RGBA', self.__imageLayers['PassiveLayer'][1].size, (255, 255, 255, 0))
        radio_grp_name = str(selected_btn).split('*')[0]

        # Select color to be filled in the polygon when its created based on Valid click event
        if Status:
            fill_color = self.__color_selected
        else:
            fill_color = (0, 0, 0, 0)

        def draw_polygon(fill_color):
            draw = ImageDraw.Draw(trans_image, "RGBA")
            draw.polygon(self.__polygon, fill_color)

        draw_polygon(fill_color=fill_color)

        if self.__drawmode == Draw_Over_Under.OVER:
            self.__savedimage = Image.alpha_composite(self.__base_image, trans_image)

        if self.__drawmode == Draw_Over_Under.UNDER:
            self.__savedimage = Image.alpha_composite(trans_image, self.__base_image)

        self.__imageLayers["Radio_Style1*" + radio_grp_name][1] = self.__savedimage

        combined_image = self.__imageLayers["PassiveLayer"][1]

        for key in self.__imageLayers:
            combined_image = Image.alpha_composite(combined_image, self.__imageLayers[key][1])

        self.__tk_image = ImageTk.PhotoImage(combined_image)
        self.__canvas.itemconfig('baseImage', image=self.__tk_image)
        # print("Canvas Updated")
        self.__bring_polygons_to_top()
        del combined_image
        del trans_image


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
                # print(coordinates)
                break
        return coordinates
