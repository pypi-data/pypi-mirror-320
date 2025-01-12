import re
import tkinter as tk
from enum import Enum

import cv2
import numpy as np
from PIL import Image, ImageTk


class SliderUPPERLOWER(Enum):
    UPPER = True
    LOWER = False


class SliderGaugeS1:
    def __init__(self, root, canvas, slider_name, needle_only_paths:list, polygon, upper_slider_range:list, lower_slider_range:list,
                 dual_mode=False, resolution=0.1, x_offset_correction=0, command=None):
        self.__command = command
        self.__root = root
        self.__canvas = canvas
        self.__polygon = polygon
        self.__tag = slider_name
        self.__resolution = resolution
        self.__decimal_places = self.__count_decimal_places(self.__resolution)

        # starts with upper scale by default
        self.__scale_upper_in_use = True
        self.__dual_mode = dual_mode
        self.__x_offset_correction = x_offset_correction

        # lowerScaleVal should be the lowest value that is marked on the gauge image
        self.__lowerScaleVal = upper_slider_range[0]
        # highScaleVal should be the highest value that is marked on the gauge image
        self.__highScaleVal = upper_slider_range[1]

        # Copy of first list item
        self.__upper_slider_min = upper_slider_range[0]
        self.__upper_slider_max = upper_slider_range[1]

        # Copy of second list item
        self.__lower_slider_min = lower_slider_range[0]
        self.__lower_slider_max = lower_slider_range[1]

        self.__needle_image_upper = Image.open(needle_only_paths[0])

        # Copy of second item in the list
        self.__needle_image_lower = Image.open(needle_only_paths[1])
        self.__image_tag = 'sliderneedleImage_' + str(slider_name)
        self.__needle_image_width, self.image_height = self.__needle_image_upper.size

        self.__tk_image_upper = ImageTk.PhotoImage(self.__needle_image_upper)
        self.__tk_image_lower = ImageTk.PhotoImage(self.__needle_image_lower)

        canvas.create_image(0, 0, anchor=tk.NW, image=self.__tk_image_upper, tags=self.__image_tag)

        self.__draw_polygon()

        #
        # points = np.array(self.polygon, dtype=np.int32)
        # self.control_x_offset, self.location_y_offset, self.rect_width, self.rect_height = cv2.boundingRect(points)
        self.__control_x_offset = self.__find_min_x(self.__polygon)
        self.__rect_width = self.__find_max_x(self.__polygon) - self.__control_x_offset
        self.__location_y_offset = self.__find_min_y(self.__polygon)

        self.__units_per_pixel = (self.__highScaleVal - self.__lowerScaleVal) / self.__rect_width

        # To record x coord of last clicked position

        # make needle visible at the beginning of the scale
        self.__last_x_location = self.__control_x_offset
        self.__last_slider_value = self.__update_needle_location(self.__control_x_offset)

    def __find_min_x(self, coordinates):  # Extract the x values from the list of coordinates
        x_values = [x for x, y in coordinates]  # Find the minimum x value
        min_x = min(x_values)
        return min_x

    def __find_min_y(self, coordinates):  # Extract the x values from the list of coordinates
        y_values = [y for x, y in coordinates]  # Find the minimum x value
        min_y = min(y_values)
        return min_y

    def __find_max_x(self, coordinates):
        # Extract the x values from the list of coordinates
        x_values = [x for x, y in coordinates]
        # Find the maximum x value
        max_x = max(x_values)
        return max_x


    def set(self, slider: SliderUPPERLOWER, value: float):
        OK_to_change = False

        if (self.__scale_upper_in_use and slider == SliderUPPERLOWER.UPPER
                and (self.__upper_slider_min <= value <= self.__upper_slider_max)):
            OK_to_change = True
            new_slider_location = self.__scale_number(self.__last_slider_value, self.__lowerScaleVal, self.__highScaleVal,
                                                      self.__control_x_offset, self.__control_x_offset + self.__rect_width)
            self.__last_x_location = new_slider_location
            self.__last_slider_value = self.__update_needle_location(self.__last_x_location)

        # If dual range is enabled then change scale in use to lower before updating slider
        if (self.__dual_mode and slider == SliderUPPERLOWER.LOWER and self.__scale_upper_in_use
                and (self.__lower_slider_min <= value <= self.__lower_slider_max)):

            OK_to_change = True

            self.__scale_upper_in_use = False
            self.__highScaleVal = self.__lower_slider_max
            self.__lowerScaleVal = self.__lower_slider_min
            self.__canvas.itemconfig(self.__image_tag, image=self.__tk_image_lower)
            new_slider_location = self.__scale_number(self.__last_slider_value, self.__lowerScaleVal, self.__highScaleVal,
                                                      self.__control_x_offset, self.__control_x_offset + self.__rect_width)
            self.__last_x_location = new_slider_location
            self.__last_slider_value = self.__update_needle_location(self.__last_x_location)


        if OK_to_change:
            new_slider_location = self.__scale_number(value, self.__lowerScaleVal, self.__highScaleVal,
                                                      self.__control_x_offset, self.__control_x_offset + self.__rect_width)
            self.__last_slider_value = self.__update_needle_location(new_slider_location)
            self.__last_x_location = new_slider_location


    @property
    def Value(self):
        return self.__last_slider_value

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


    def __slider_mouse_dn(self, event):
        x, y = event.x, event.y

        if self.__is_point_in_polygon(x, y, self.__polygon):
            self.__last_slider_value = self.__update_needle_location(x)
            new_slider_value = self.__scale_number(self.__last_slider_value, self.__lowerScaleVal, self.__highScaleVal,
                                                   self.__control_x_offset, self.__control_x_offset + self.__rect_width)
            self.__last_x_location = new_slider_value

    def __slider_Right_mouse_dn(self, event):
        x, y = event.x, event.y

        if self.__dual_mode and self.__is_point_in_polygon(x, y, self.__polygon):

            if self.__scale_upper_in_use:
                self.__scale_upper_in_use = False
                self.__highScaleVal = self.__lower_slider_max
                self.__lowerScaleVal = self.__lower_slider_min
                self.__canvas.itemconfig(self.__image_tag, image=self.__tk_image_lower)
                self.__last_slider_value = self.__update_needle_location(self.__last_x_location)
                new_slider_location = self.__scale_number(self.__last_slider_value, self.__lowerScaleVal, self.__highScaleVal,
                                                          self.__control_x_offset, self.__control_x_offset + self.__rect_width)
                self.__last_x_location = new_slider_location
            else:
                self.__scale_upper_in_use = True
                self.__highScaleVal = self.__upper_slider_max
                self.__lowerScaleVal = self.__upper_slider_min
                self.__canvas.itemconfig(self.__image_tag, image=self.__tk_image_upper)
                self.__last_slider_value = self.__update_needle_location(self.__last_x_location)

                new_slider_location = self.__scale_number(self.__last_slider_value, self.__lowerScaleVal, self.__highScaleVal,
                                                          self.__control_x_offset, self.__control_x_offset + self.__rect_width)
                self.__last_x_location = new_slider_location

    def __slider_mouse_wheel(self, event):
        x, y = event.x, event.y
        mouse_wheel_direction = None
        if event.delta > 0:
            mouse_wheel_direction = 'up'
        else:
            mouse_wheel_direction = 'dn'


        if self.__is_point_in_polygon(x, y, self.__polygon):
            new_slider_value = None
            if mouse_wheel_direction == 'up':
                new_slider_value = (self.__last_slider_value + self.__resolution) \
                    if ((self.__last_slider_value + self.__resolution) < self.__highScaleVal) \
                    else self.__highScaleVal
            else:
                new_slider_value = (self.__last_slider_value - self.__resolution) \
                    if ((self.__last_slider_value - self.__resolution) > self.__lowerScaleVal) \
                    else self.__lowerScaleVal

            # new_slider_value = round(new_slider_value, self.decimal_places)
            new_slider_value = round(new_slider_value / self.__resolution) * self.__resolution

            self.__last_slider_value = new_slider_value
            new_slider_location = self.__scale_number(new_slider_value, self.__lowerScaleVal, self.__highScaleVal,
                                                      self.__control_x_offset, self.__control_x_offset + self.__rect_width)
            slider_loc_after_update = self.__update_needle_location(new_slider_location)
            self.__last_x_location = new_slider_location

    def __count_decimal_places(self, number):
        count = 0
        while number != int(number):
            number *= 10
            count += 1
        return count

    def __slider_drag_value_update(self, value):
        pass

    def __draw_polygon(self):
        self.__canvas.create_polygon(self.__polygon, fill='', outline='', tags=self.__tag, width=0)
        self.__canvas.tag_bind(self.__tag, '<Button-1>', self.__slider_mouse_dn)
        self.__canvas.bind('<MouseWheel>', self.__slider_mouse_wheel, add='+')
        self.__canvas.tag_bind(self.__tag, '<Button-3>', self.__slider_Right_mouse_dn)

    def __update_needle_location(self, x):
        self.__canvas.coords(self.__image_tag, x + self.__x_offset_correction - self.__needle_image_width // 2,
                             self.__location_y_offset)
        number_to_be_rounded = self.__scale_number(x, self.__control_x_offset, self.__control_x_offset + self.__rect_width,
                                                   self.__lowerScaleVal, self.__highScaleVal)

        return_val = round(number_to_be_rounded / self.__resolution) * self.__resolution

        if self.__command is not None:

            if self.__scale_upper_in_use:
                preceding_text = str(self.__tag) + "," + "UpperSlider,"
            else:
                preceding_text = str(self.__tag) + "," + "Lower_Slider,"

            self.__command(preceding_text + str(round(return_val, 5)))

        return return_val

    def __scale_number(self, value: float, x_min: float, x_max: float, y_min: float, y_max: float):
        m = (y_max - y_min) / (x_max - x_min)
        b = y_min - m * x_min
        return (m * value) + b


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