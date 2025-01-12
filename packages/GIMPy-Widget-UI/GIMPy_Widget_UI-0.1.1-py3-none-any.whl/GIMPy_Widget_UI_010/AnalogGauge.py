import ast
import csv
import tkinter as tk
import re

from PIL import Image, ImageTk

class AnalogGauge:
    def __init__(self, root, canvas, needle_only_path, needle_centroid_x: int, needle_centroid_y: int,
                 lowerScaleVal: float, higherScaleVal: float, maxAngle:float, needle_tag: str, init_rotation_angle=0,
                 command=None):
        self.__root = root
        self.__canvas = canvas
        self.__command = command
        # In the gauge+needle overlayed image, if needle coincides with the lowest value then minAngle is 0.
        # Assumption here is that this will always be the case.
        self.__minAngle = 0
        self.__maxAngle = maxAngle

        self.__needle_tag = needle_tag
        # lowerScaleVal is the lowest value that is marked on the gauge image
        self.__lowerScaleVal = lowerScaleVal
        # highScaleVal is the highest value that is marked on the gauge image
        self.__highScaleVal = higherScaleVal

        self.__needle_image = Image.open(needle_only_path)
        self.__needle_image = self.__needle_image.rotate(-1 * init_rotation_angle)

        self.__image_width, self.image_height = self.__needle_image.size
        self.__needle_center_x = needle_centroid_x
        self.__needle_center_y = needle_centroid_y
        self.__tk_image = ImageTk.PhotoImage(self.__needle_image)
        # make needle visible once an instance is created
        self.__update_gauge_needle(self.__lowerScaleVal)
        self.__last_value = self.__lowerScaleVal


    def __update_gauge_needle(self, value: float):
        # Positive angles rotates the image anticlockwise and negative angle parameter goes clockwise
        # so for moving the needle we multiply with -1 after angle calculation to rotate the needle clockwise
        angle = self.__calculate_angle(value)
        rotated_image = self.__needle_image.rotate(angle, resample=Image.BICUBIC, expand=True)
        self.__tk_image = ImageTk.PhotoImage(rotated_image)
        self.__canvas.itemconfig(self.__needle_tag, image=self.__tk_image)
        self.__last_value = value

        if self.__command is not None:
            self.__command(angle)
        # self.canvas.gauge_image = self.tk_image  # Keep a reference to the image

    def __calculate_angle(self, value):
        return self.__scale_number(int(value), self.__lowerScaleVal, self.__highScaleVal, self.__minAngle, self.__maxAngle)

    def __scale_number(self, value, lowScaleVal, highscaleval, minangle, maxangle):
        scaled_value = ((int(value) - lowScaleVal) / (highscaleval - lowScaleVal)) * (maxangle - minangle) + minangle
        return scaled_value * -1

    def set(self, value):
        self.__update_gauge_needle(value)

    def set_angle(self, value):
        """
        Recommended to use this only once at the time of creating object
        :param value: angle in degrees
        :return: None
        """
        angle = -1 * value if 0 <= value <= 360 else 0
        rotated_image = self.__needle_image.rotate(angle, resample=Image.BICUBIC, expand=True)
        self.__tk_image = ImageTk.PhotoImage(rotated_image)
        self.__canvas.itemconfig(self.__needle_tag, image=self.__tk_image)
        self.__needle_image = rotated_image
        self.__last_value = self.__lowerScaleVal

    @staticmethod
    def find_control_centroid(control_poly_path, control_type, control_name):
        found = False
        with open(control_poly_path, 'r') as file:
            reader = csv.reader(file, delimiter=':')
            for row in reader:
                # print(row)
                if row[0] == control_type and row[1] == control_name:
                    result_tuple = ast.literal_eval(row[2])
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