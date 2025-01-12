import ast
import csv
import re
import tkinter as tk
from enum import Enum

import cv2
import numpy as np
from PIL import Image, ImageTk

from GIMPy_Widget_UI import AnalogGauge as agauge

class SliderUPPERLOWER(Enum):
    UPPER = True
    LOWER = False


class KnobS1:
    def __init__(self, root, canvas, knob_name, knob_path, polygon, knob_x_y:list, knob_range:list, max_angle,
                 resolution=0.1, x_offset_correction=0, init_angle_rotation=0, command=None):
        self.__command = command
        self.__root = root
        self.__knob_name = knob_name
        self.__canvas = canvas
        self.__polygon = polygon
        self.__tag = knob_name
        self.__knob_path = knob_path
        self.__resolution = resolution
        self.__x_loc, self.__y_loc = knob_x_y[0], knob_x_y[1]
        self.__init_angle_rotation = init_angle_rotation
        # starts with upper scale by default
        self.__scale_upper_in_use = True
        self.__x_offset_correction = x_offset_correction

        # lowerScaleVal should be the lowest value that is marked on the gauge image
        self.__lowerScaleVal = knob_range[0]
        # highScaleVal should be the highest value that is marked on the gauge image
        self.__highScaleVal = knob_range[1]

        # Copy of first list item
        self.__knob_min = knob_range[0]
        self.__knob_max = knob_range[1]
        self.__max_angle = max_angle

        # Copy of second list item
        self.__lower_slider_min = 0
        self.__lower_slider_max = 0

        # dc_amp_needle_path = 'DC_Amp_Needle.png'
        self.__knob_image = Image.open(self.__knob_path).convert("RGBA")
        self.__knob_photo = ImageTk.PhotoImage(self.__knob_image)
        self.__knob_tag_name = f'tag_{self.__knob_name}'
        canvas.create_image(self.__x_loc, self.__y_loc, anchor=tk.CENTER, image=self.__knob_photo,
                            tags=self.__knob_tag_name)

        self.__knob = agauge(root, canvas, knob_path, self.__x_loc, self.__y_loc, self.__knob_min,
                              self.__knob_max, self.__max_angle, self.__knob_tag_name,
                             init_rotation_angle=init_angle_rotation)
        # self.__knob.set_angle(self.__init_angle_rotation)

        self.__current_value = self.__knob_min
        self.__draw_polygon()


    def set(self, value: float):
        self.__current_value = value if (self.__knob_min <= value <= self.__knob_max) else self.__current_value
        self.__knob.set(self.__current_value)


    @property
    def Value(self):
        return self.__current_value

    def __is_point_in_polygon(self, x, y, points):
        """
        Function that returns True if x,y falls either in or on the list of points, False otherwise
        :param x: x coordinate
        :param y:  y coordinate
        :param points: List of coordinates
        :return: True if x,y falls either in or on the list of points, False otherwise
        """
        # Convert points to a format suitable for cv2.pointPolygonTest
        contour = np.array(points, dtype=np.int32)
        # if the point is "in" or "on" the polygon then return True
        return cv2.pointPolygonTest(contour, (x, y), False) >= 0


    def __slider_mouse_wheel(self, event):
        x, y = event.x, event.y
        mouse_wheel_direction = None
        if event.delta > 0:
            mouse_wheel_direction = 'up'
        else:
            mouse_wheel_direction = 'dn'

        if self.__is_point_in_polygon(x, y, self.__polygon):
            if mouse_wheel_direction == 'up':
                self.__current_value = self.__current_value + self.__resolution \
                    if self.__current_value + self.__resolution < self.__knob_max \
                    else self.__knob_max
            else:
                self.__current_value = self.__current_value - self.__resolution \
                    if self.__current_value - self.__resolution > self.__knob_min \
                    else self.__knob_min

            self.__current_value = round(self.__current_value / self.__resolution) * self.__resolution

            self.__knob.set(self.__current_value)

            if self.__command is not None:
                self.__command(self.__current_value)


    def __draw_polygon(self):
        self.__canvas.create_polygon(self.__polygon, fill='', outline='', tags=self.__tag, width=0)
        self.__canvas.bind('<MouseWheel>', self.__slider_mouse_wheel, add='+')


    @staticmethod
    def find_control_centroid(control_poly_path, control_type, control_name):
        found = False
        with open(control_poly_path, 'r') as file:
            reader = csv.reader(file, delimiter=':')
            for row in reader:
                # print(row)
                if row[0] == control_type and row[1] == control_name:
                    result_tuple = ast.literal_eval(row[2])
                    found = True
                    # The format of centroid in the file is List of a single tuple
                    return result_tuple[0]
        if not found:
            raise ValueError(f"Control type={control_type} or Control Name={control_name} not "
                             f"found in {control_poly_path}")
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