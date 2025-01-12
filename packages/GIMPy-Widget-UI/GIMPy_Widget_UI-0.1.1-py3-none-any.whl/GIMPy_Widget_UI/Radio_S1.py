import tkinter as tk
import re

from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np


class RadioS1:
    def __init__(self, radioBtnName, canvas, polygon, default=False, stipple_color=(0, 100, 0), command=None):
        self.__canvas = canvas
        self.__btnName = radioBtnName
        self.__command = command
        self.__polygon = polygon
        if polygon == None:
            raise ValueError(f"{radioBtnName} point coordinates not found...")
        self.__stipple_color = stipple_color
        self.__draw_polygon()
        # set _value to None, this is used as a getter value
        self._value = None
        if not default:
            # self.selected_Btn = radioBtnName
            self.__change_radio_selected(radioBtnName, False)
        else:
            # print(f'{radioBtnName} is set as Default')
            # self.selected_Btn = radioBtnName
            self.__change_radio_selected(radioBtnName, True)

        self.__selected_points = None

    def __load_image(self):
        # Load the image using PIL
        self.__tk_image = ImageTk.PhotoImage(self.pil_image)
        self.__canvas.create_image(0, 0, anchor=tk.NW, image=self.__tk_image, tags="TempRadioImage")

    def __draw_polygon(self):
        tag = self.__btnName
        # print(tag)
        self.__canvas.create_polygon(self.__polygon, fill='', outline='', tags=tag, width=0)
        self.__canvas.tag_bind(tag, '<ButtonPress>', self.__radio_top_layer_mouse_dn)
        self.__canvas.tag_bind(tag, '<ButtonRelease>', self.__radio_top_layer_mouse_up)

    def __rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

    def __buttonpresseffect(self, btn_name, enable_effect):
        if enable_effect:
            self.__canvas.itemconfig(btn_name, fill=self.__rgb_to_hex((230, 190, 130)), stipple='gray50')
        else:
            self.__canvas.itemconfig(btn_name, fill='')

    def __radio_top_layer_mouse_dn(self, event):
        x, y = event.x, event.y

        if self.__is_point_in_polygon(x, y, self.__polygon):
            closesttag = self.__canvas.find_closest(event.x, event.y)
            tag_name = self.__canvas.gettags(closesttag)
            self.selected_Btn = tag_name[0]
            self.__selected_points = self.__polygon
            # self.buttonpresseffect(self.selected_Btn, True)
            # print(f"Mouse Down: Clicked {tag_name} inside polygon at ({x}, {y})")

    def __radio_top_layer_mouse_drag(self, event):
        x, y = event.x, event.y
        closesttag = self.__canvas.find_closest(event.x, event.y)
        tag_name = self.__canvas.gettags(closesttag)

        # if tuple tag_name is empty that means the mouse is outside the button area
        if not len(tag_name):
            self.__buttonpresseffect(self.selected_Btn, False)
        else:
            if self.selected_Btn == tag_name[0]:
                self.__buttonpresseffect(self.selected_Btn, True)
            else:
                self.__buttonpresseffect(self.selected_Btn, False)

    def __radio_top_layer_mouse_up(self, event):
        x, y = event.x, event.y
        closesttag = self.__canvas.find_closest(event.x, event.y)
        tag_name = self.__canvas.gettags(closesttag)
        # self.buttonpresseffect(self.selected_Btn, False)

        # if tuple tag_name is empty that means the mouse was released outside the button area
        if len(tag_name) and self.selected_Btn == tag_name[0]:
            # print(f"Mouse Up: Clicked inside polygon {self.selected_Btn} at ({x}, {y})")
            # print("Button selected")
            # self.select_radio(self.selected_Btn)
            self.__change_radio_selected(self.selected_Btn, True)
            if self.__command is not None:
                self.__command(self.selected_Btn)
            # Placeholder to call function that handles button press
        else:
            # print("Mouse left the button before releasing, not a valid button press")
            # print(f"Clicked outside polygon at ({x}, {y})")
            self.selected_Btn = None

        # self.findallchildren()

    def __is_point_in_polygon(self, x, y, points):
        # Convert points to a format suitable for cv2.pointPolygonTest
        contour = np.array(points, dtype=np.int32)
        return cv2.pointPolygonTest(contour, (x, y), False) >= 0

    def __change_radio_selected(self, selected_btn, new_status=False):
        # Pass selected_btn as argument to this function so that it can also be called
        # as a default button when creating an instance for a radio.
        # print(selected_btn)

        for item in self.__canvas.find_all():
            # print(self.__canvas.gettags(item))
            if (len(self.__canvas.gettags(item)) and self.__canvas.gettags(item)[0].
                    startswith(str(selected_btn).split('*')[0])):
                self.__canvas.itemconfig(item, fill='', stipple='')
        # self.bring_polygons_to_top()

        if new_status:
            self.__canvas.itemconfig(selected_btn, fill=self.__rgb_to_hex(self.__stipple_color), stipple='gray50')


    @staticmethod
    def str_to_coordinates(file_loc, control_name, parameter_offset):
        coordinates = None
        with open(file_loc, 'r') as file:
            lines = file.readlines()

        for line in lines:
            split_params = line.split(":")
            if split_params[1] == control_name:
                # print(f'str_to_coordinates - {control_name} found...')
                match = re.findall(r'\((\d+),\s*(\d+)\)', split_params[parameter_offset - 1].strip())
                coordinates = [tuple(map(int, coord)) for coord in match]
                # print(coordinates)
                break

        if coordinates is None:
            raise ValueError(f"Control Name={control_name} not found in {file_loc}")

        return coordinates
