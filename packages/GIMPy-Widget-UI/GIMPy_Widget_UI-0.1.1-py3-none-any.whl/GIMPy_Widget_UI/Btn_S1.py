import re
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np


class Btn_S1:
    def __init__(self, btnName, canvas, btn_shape_points, press_drag_color = (255, 255, 255), command=None):
        # self.root = root
        self.__canvas = canvas
        self.__btnName = btnName
        # self.image_path = image_path
        self.__btn_shape_points = btn_shape_points
        self.__selected_Btn = None
        self.__command = command
        self.__press_drag_color = press_drag_color
        self.__draw_btn_shape()

    def __load_image(self):
        # Load the image using PIL
        pil_image = Image.open(self.image_path)
        self.__tk_image = ImageTk.PhotoImage(pil_image)
        self.__canvas.create_image(0, 0, anchor=tk.NW, image=self.__tk_image)

    def __draw_btn_shape(self):
        tag = self.__btnName
        # print(tag)
        self.__canvas.create_polygon(self.__btn_shape_points, fill='', outline='', tags=tag, width=0)
        self.__canvas.tag_bind(tag, '<Button-1>', self.__top_layer_mouse_dn)
        self.__canvas.tag_bind(tag, '<ButtonPress>', self.__top_layer_mouse_dn)
        self.__canvas.tag_bind(tag, '<B1-Motion>', self.__top_layer_mouse_drag)
        self.__canvas.tag_bind(tag, '<ButtonRelease>', self.__top_layer_mouse_up)


    def __rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

    def __buttonpresseffect(self, btn_name, enable_effect):
        # stipple_file = "@Raw Images for Sample GUI/Layered_Groups/ClassDemoImages/Tick_Mark_XBM.xbm"
        if enable_effect:
            self.__canvas.itemconfig(btn_name, fill=self.__rgb_to_hex(self.__press_drag_color), stipple='gray25')
            # self.canvas.itemconfig(btn_name, fill=self.rgb_to_hex((230, 190, 130)), stipple=stipple_file)
        else:
            self.__canvas.itemconfig(btn_name, fill='')


    def __top_layer_mouse_dn(self, event):
        x, y = event.x, event.y

        if self.__is_point_in_polygon(x, y, self.__btn_shape_points):
            closesttag = self.__canvas.find_closest(event.x, event.y)
            tag_name = self.__canvas.gettags(closesttag)
            self.__selected_Btn = tag_name[0]
            self.__buttonpresseffect(self.__selected_Btn, True)


    def __top_layer_mouse_drag(self, event):
        x, y = event.x, event.y
        closesttag = self.__canvas.find_closest(event.x, event.y)
        tag_name = self.__canvas.gettags(closesttag)

        # if tuple tag_name is empty that means the mouse is outside the button area
        if not len(tag_name):
            self.__buttonpresseffect(self.__selected_Btn, False)
        else:
            if self.__selected_Btn == tag_name[0]:
                self.__buttonpresseffect(self.__selected_Btn, True)
            else:
                self.__buttonpresseffect(self.__selected_Btn, False)

    def __top_layer_mouse_up(self, event):
        x, y = event.x, event.y
        closesttag = self.__canvas.find_closest(event.x, event.y)
        tag_name = self.__canvas.gettags(closesttag)

        if len(tag_name) and self.__selected_Btn == tag_name[0]:
            if self.__command is not None:
                self.__command(self.__selected_Btn)
            # Placeholder to call function that handles button press
        else:
            self.__selected_Btn = None

        self.__buttonpresseffect(self.__selected_Btn, False)

    def __is_point_in_polygon(self, x, y, points):
        # Convert points to a format suitable for cv2.pointPolygonTest
        contour = np.array(points, dtype=np.int32)
        return cv2.pointPolygonTest(contour, (x, y), False) >= 0

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
