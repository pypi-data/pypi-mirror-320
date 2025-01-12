import ast
import csv
import re
import tkinter as tk
from enum import Enum

import cv2
import numpy as np
from PIL import Image, ImageTk
from PIL import ImageDraw


class CheckBox_S2:
    def __init__(self, canvas, checkbox_btn_name, base_imagesize, base_image, polygon: list, checkbox_on_off_image_path: list,
                 checkbox_centroid: tuple,
                 default_state_is_on=False, x_offset_correction=0, y_offset_correction=0, command=None):
        self.__tk_image = None
        self.__command = command
        self.__canvas = canvas
        self.__polygon = polygon
        self.__base_image_size = base_imagesize
        self.__base_image = base_image
        self.__x_offset_correction = x_offset_correction
        self.__y_offset_correction = y_offset_correction

        self.__checkbox_centroid = checkbox_centroid

        self.__btnName = checkbox_btn_name
        self.__tag = checkbox_btn_name
        self.__clicked_checkbox = None

        self.__default_state_is_on = default_state_is_on
        self.__x_offset_correction = x_offset_correction

        self.__selected_image = Image.open(checkbox_on_off_image_path[0])
        self.__unselected_image = Image.open(checkbox_on_off_image_path[1])

        self.__image_tag_selected = 'checkbox_img_tag_selected_' + self.__tag
        self.__image_tag_unselected = 'checkbox_img_tag_unselected_' + self.__tag

        # self.on_off_image_width, self.on_off_image_height = self.on_off_image.size
        self.__selected_photo = ImageTk.PhotoImage(self.__selected_image)
        self.__unselected_photo = ImageTk.PhotoImage(self.__unselected_image)

        __checkbox_centroid_x, __checkbox_centroid_y = checkbox_centroid[0], checkbox_centroid[1]

        self.__canvas.create_image(__checkbox_centroid_x, __checkbox_centroid_y,
                                   anchor=tk.CENTER, image=self.__selected_photo, tags=self.__image_tag_selected)
        self.__canvas.create_image(__checkbox_centroid_x, __checkbox_centroid_y,
                                   anchor=tk.CENTER, image=self.__unselected_photo, tags=self.__image_tag_unselected)

        self.__draw_polygon()
        self.__last_status = not default_state_is_on
        self.__toggle_checkbox()


    def set(self, state: bool):
        state=not state # toggle_checkbox function toggles the input so 'state' is reversed here

        if self.__last_status == state:
            self.__last_status = state
            self.__toggle_checkbox()


    @property
    def Value(self):
        return True if self.__last_status else False


    def __checkbox_mouse_dn(self, event):
        # As thie mouse down is only triggered when it's clicked in one of the two button positions so
        # no need to check whether the click has occurred within the polygon, just toggle is required
        x, y = event.x, event.y

        if self.__is_point_in_polygon(x, y, self.__polygon):
            closesttag = self.__canvas.find_closest(event.x, event.y)
            tag_name = self.__canvas.gettags(closesttag)
            self.__clicked_checkbox = tag_name[0]

    def __checkbox_mouse_hover(self, event):
        x, y = event.x, event.y
        self.__add_remove_skin(True)

    def __checkbox_mouse_leave(self, event):
        # print("Mouse Leaves")
        self.__add_remove_skin(False)

    def __checkbox_mouse_up(self, event):
        x, y = event.x, event.y
        closesttag = self.__canvas.find_closest(event.x, event.y)
        tag_name = self.__canvas.gettags(closesttag)

        # if tuple tag_name is empty that means the mouse was released outside the button area
        if len(tag_name) and self.__clicked_checkbox == tag_name[0]:
            self.__add_remove_skin(False)
            self.__toggle_checkbox()

    def __add_remove_skin(self, status: bool):
        trans_image = Image.new('RGBA', self.__base_image_size, (255, 255, 255, 0))
        fill_color = None

        # Select color to be filled in the polygon when its created based on Valid click event
        if status:
            fill_color = (0, 0, 255, 100)
        else:
            fill_color = (0, 0, 0, 0)

        def draw_polygon(fill_color):
            draw = ImageDraw.Draw(trans_image, "RGBA")
            draw.polygon(self.__polygon, fill_color)

        draw_polygon(fill_color=fill_color)

        saved_image = Image.alpha_composite(self.__base_image, trans_image)

        combined_image = saved_image

        self.__tk_image = ImageTk.PhotoImage(combined_image)
        self.__canvas.itemconfig('baseImage', image=self.__tk_image)
        del combined_image
        del trans_image


    def __toggle_checkbox(self):
        if self.__last_status:
            self.__canvas.itemconfig(self.__image_tag_selected, state='hidden')
            self.__canvas.itemconfig(self.__image_tag_unselected, state='normal')
            self.__last_status = False
        else:
            self.__canvas.itemconfig(self.__image_tag_selected, state='normal')
            self.__canvas.itemconfig(self.__image_tag_unselected, state='hidden')
            self.__last_status = True

        if self.__command is not None:
            self.__command(f"{self.__tag}:{self.__last_status}")

    def __is_point_in_polygon(self, x, y, points):
        # Convert points to a format suitable for cv2.pointPolygonTest
        contour = np.array(points, dtype=np.int32)
        return cv2.pointPolygonTest(contour, (x, y), False) >= 0


    def __draw_polygon(self):
        self.__canvas.create_polygon(self.__polygon, fill='', outline='', tags=self.__tag, width=0)
        self.__canvas.tag_bind(self.__tag, '<Button-1>', self.__checkbox_mouse_dn)
        self.__canvas.tag_bind(self.__tag, '<ButtonRelease>', self.__checkbox_mouse_up)
        self.__canvas.tag_bind(self.__tag, '<Enter>', self.__checkbox_mouse_hover)
        self.__canvas.tag_bind(self.__tag, '<Leave>', self.__checkbox_mouse_leave)


    @staticmethod
    def find_control_centroid(control_pos_path, control_type, control_name):
        with open(control_pos_path, 'r') as file:
            found = False
            reader = csv.reader(file, delimiter=':')
            for row in reader:
                # print(row)
                if row[0] == control_type and row[1] == control_name:
                    result_tuple = ast.literal_eval(row[2])
                    # The format of centroid in the file is List of a single tuple
                    return result_tuple[0]

        if not found:
            raise ValueError(f"Control type={control_type} or Control Name={control_name} not "
                             f"found in {control_pos_path}")

        return None


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
