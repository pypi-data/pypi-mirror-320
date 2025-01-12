import sys

import cv2
# import numpy as np
from tkinter import Tk, Canvas, Entry, filedialog
from PIL import Image, ImageTk
import tkinter as tk

def map_gimpy():
    # Function to handle mouse click events
    def on_click(event):
        remove_all_entry_boxes()
        root.title(f"Map controls to Python - clicked outside active area")
        # contour_label.set(f"Map controls to Python - clicked outside active area")
        x, y = event.x, event.y

        for i, contour in enumerate(contours):
            if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
                # contour_label.set(f"Item Number: {i + 1}")
                root.title(f"Map controls to Python, Right click item {i+1} to map controls")
                break


    def remove_all_entry_boxes():
        enter_Instances = []
        for child in root.winfo_children():
            if isinstance(child, Entry):
                enter_Instances.append(child)
                e = str(child.winfo_name())[1:]
                print(e)

        for entry in enter_Instances:
            entry.destroy()


    def rightclick_input_box(event):

        def on_enter(e):
            global user_input
            user_input = entry.get()
            # contour_label.set(f"You entered: {user_input}")
            # print(temp_list)
            centroid = (cX, cY)
            # file_path = filedialog.asksaveasfilename(defaultextension=".txt",
            #                                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

            file_path = control_positions_file

            if file_path:
                with open(file_path, 'a') as file:
                    file.write(str(user_input) + ":" + "[" + str(centroid) + "]:" + str(temp_list))
                    file.write('\n')
                    file.close()

            entry.destroy()

        # To make sure there is only one Entry box that is active at any given time
        remove_all_entry_boxes()

        x, y = event.x, event.y
        for i, contour in enumerate(contours):
            if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
                temp_list.clear()
                for point in contour:
                    for x, y in point:
                        temp_list.append((int(x), int(y)))
                M = cv2.moments(contour)

                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    cX, cY = 0, 0

                entry = Entry(root)
                entry.place(x=cX, y=cY)
                # Focus on the entry widget
                entry.focus_set()
                # Bind the Enter key to store the input and close the input box
                entry.bind("<Return>", on_enter)
                break


    # Load the "...Negative" image

    image = None
    neg_file_path = filedialog.askopenfilename(title="Open Active file", filetypes=[("...Active image file", "*.png"), ("All files", "*.*")])
    if neg_file_path:
        image = cv2.imread(neg_file_path)
    else:
        sys.exit("No file selected, quitting...")

    preview_file_path = filedialog.askopenfilename(title="Load Passive image file",
                                                   filetypes=[("Passive image file", "*.png"), ("All files", "*.*")])

    if not preview_file_path:
        sys.exit("No file selected, quitting...")

    control_positions_file = filedialog.askopenfilename(title="Load control positions file",
                                                    filetypes=[("Controls Position file", "*.txt"), ("All files", "*.*")])

    if not control_positions_file:
        sys.exit("No file selected, quitting...")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edged = cv2.Canny(blurred, 10, 190)

    # Find contours
    contours, heirarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours = sorted(contours, key=cv2.contourArea, reverse=True)

    contourList = []
    xyPoints = []
    temp_list = []
    i = 0

    # with open('Output.txt', 'w') as file:
    #     file.write("")
    #     file.close()

    for contour in contours:
        i += 1
        # print(i)
        temp_list.clear()
        xyPoints.clear()
        for point in contour:
            for x, y in point:
                xyPoints.append(int(x))
                xyPoints.append(int(y))
                tpl = (int(x), int(y))
                temp_list.append(tpl)
            contourList.append(temp_list)
        # print(temp_list)
        # print(xyPoints)

        with open('Output.txt', 'a') as file:
            file.write("\"Item" + str(i) + "\"" + ":")
            file.write(str(temp_list))
            if i != len(contours):
                file.write(",")
            file.close()
    # contourList.clear()
    contour_points = [tuple(point[0]) for contour in contours for point in contour]
    converted_points = [(int(x), int(y)) for x, y in contour_points]
    one_dimensional_list = [coordinate for point in converted_points for coordinate in point]
    #print(contour_points)
    # Sort contours by area
    contours = sorted(contours, key=cv2.contourArea)

    # Draw contours and label them
    for i, contour in enumerate(contours):
        cv2.drawContours(image, [contour], -1, (0, 155, 250), 1)
        M = cv2.moments(contour)

        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0
        cv2.circle(image, (cX, cY), 2, (255, 255, 255), 2)
        # cv2.putText(image, str(i + 1), (cX - 10, cY + 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 250), 1)

        # Read control position file and put a label if a control has already been defined

    # Convert the image to RGB (OpenCV uses BGR by default)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)

    root = Tk()
    active_layer_image = ImageTk.PhotoImage(image_pil)
    image_pil.save("Detected_Output.png")


    top_image = Image.open(preview_file_path)
    passive_layer_image = ImageTk.PhotoImage(top_image)

    # Create a Tkinter window
    root_width, root_height = top_image.size
    root_geometry = str(root_width) + "x" + str(root_width)
    root.geometry(root_geometry)
    root.title("Map controls to Python")

    canvas = Canvas(root, width=1920, height=1080)
    canvas_image = canvas.create_image(0, 0, anchor=tk.NW, image=passive_layer_image)
    canvas.place(x=0, y=0)
    # canvas.pack()


    canvas.bind("<Button-1>", on_click)

    user_input = ""
    canvas.bind("<Button-3>", rightclick_input_box)

    # put a label where ever a currently detected centroid already exists in the position file
    with open(control_positions_file, 'r') as file:
        lines = file.readlines()
        for i, contour in enumerate(contours):
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                search_tuple = (cX, cY)

                for line in lines:
                    if str(search_tuple) in line:
                        btn_attributes_lst = line.split(':')
                        print(search_tuple)
                        label = tk.Label(text=str(btn_attributes_lst[0] + ':' + btn_attributes_lst[1]))
                        label.place(x=cX+10, y=cY)
        file.close()

    def selectscreens(event):
        if event.keysym == 'F1':
            print("F1")
            canvas.itemconfig(canvas_image, image=active_layer_image)
        else:
            print("F2")
            canvas.itemconfig(canvas_image, image=passive_layer_image)


    root.bind('<F1>', selectscreens)
    root.bind('<F2>', selectscreens)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    map_gimpy()