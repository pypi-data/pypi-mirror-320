import ast
import csv
import re
import tkinter as tk
from enum import Enum

import cv2
import numpy as np
from PIL import Image, ImageTk


class On_Off_Button:
    def __init__(self, canvas, on_off_btn_name: str, on_off_polygon: list, button_only_image_path, on_off_centroids: list,
                 default_state_is_on=False, command=None):

        self.__command = command
        self.__canvas = canvas

        if len(on_off_polygon) > 2:
            raise ValueError(f"Expected 2, found {len(on_off_polygon)} items in the list for ON_OFF button={on_off_btn_name}")

        if None in on_off_polygon:
            raise ValueError(f"Point coordinates not found for ON_OFF button={on_off_btn_name}")

        self.__on_polygon = on_off_polygon[0]
        self.__off_polygon = on_off_polygon[1]

        if any(not isinstance(centroid, tuple) for centroid in on_off_centroids):
            raise ValueError(f"All centroid values in ON_OFF button={on_off_btn_name} list are expected to be tuples")

        self.__on_centroid = on_off_centroids[0]
        self.__off_centroid = on_off_centroids[1]

        self.__tag = on_off_btn_name

        self.__default_state_is_on = default_state_is_on

        self.__on_off_image_path = button_only_image_path
        self.__on_off_image = Image.open(self.__on_off_image_path)

        self.__image_tag = 'On_Off_img_' + self.__tag
        self.__on_off_image_width, self.on_off_image_height = self.__on_off_image.size
        self.__on_off_photo = ImageTk.PhotoImage(self.__on_off_image)

        # print(self.__on_centroid)

        canvas.create_image(self.__on_centroid[0] if default_state_is_on else self.__off_centroid[0],
                            self.__on_centroid[1] if default_state_is_on else self.__off_centroid[1],
                            anchor=tk.CENTER, image=self.__on_off_photo, tags=self.__image_tag)

        # print(self.__canvas.coords(self.__image_tag))

        self.__draw_polygons()


    def set(self, state: bool):
        if state==True:
            self.__canvas.coords(self.__image_tag, self.__on_centroid[0], self.__on_centroid[1])
        else:
            self.__canvas.coords(self.__image_tag, self.__off_centroid[0], self.__off_centroid[1])


    @property
    def Value(self):
        return True if self.__canvas.coords(self.__image_tag) == list(self.__on_centroid) else False

    def __ON_OFF_mouse_dn(self, event):
        # As thie mouse down is only triggered when it's clicked in one of the two button positions so
        # no need to check whether the click has occurred within the polygon, just toggle is required

        if list(self.__on_centroid) == self.__canvas.coords(self.__image_tag):
            x = self.__off_centroid[0]
            y = self.__off_centroid[1]
            self.__canvas.coords(self.__image_tag, x, y)
            if self.__command is not None:
                self.__command(f"{self.__tag}:{False}")
        else:
            x = self.__on_centroid[0]
            y = self.__on_centroid[1]
            self.__canvas.coords(self.__image_tag, x, y)

            if self.__command is not None:
                self.__command(f"{self.__tag}:{True}")


    def __draw_polygons(self):
        self.__canvas.create_polygon(self.__on_polygon, fill='', outline='', tags=self.__tag, width=0)
        self.__canvas.create_polygon(self.__off_polygon, fill='', outline='', tags=self.__tag, width=0)
        self.__canvas.tag_bind(self.__tag, '<Button-1>', self.__ON_OFF_mouse_dn)


    @staticmethod
    def find_control_centroid(control_poly_path, control_type, control_name):
        with open(control_poly_path, 'r') as file:
            reader = csv.reader(file, delimiter=':')
            found = False
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
