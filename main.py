# main.py

# library imports
import numpy
import matplotlib.pyplot as plt
import PySimpleGUI as sg
from astropy.time import Time as aTime
from tkinter.filedialog import asksaveasfilename as SaveFileDialog
from tkinter.colorchooser import askcolor as ColorChooser

# import of own functions and variables
import inputs as __INPUTS
import functions as __FUNCTIONS
import gui_setup as __GUI
import settings as __SETTINGS

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# INIT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# declare the plot and load a map image into the background
img = plt.imread(__SETTINGS.PATH_MAP)
p, (ax_Map, ax_Height) = plt.subplots(2, figsize=(__SETTINGS.PLOT_ONSCREEN_WIDTH, __SETTINGS.PLOT_ONSCREEN_HEIGHT), gridspec_kw={'height_ratios': [2, 1]})
ax_Map.imshow(img, extent=[-180, 180, -90, 90])
plt.setp(ax_Map, xticks=numpy.arange(start=-180, stop=181, step=30), yticks=numpy.arange(start=-90, stop=91, step=15), xlabel="latitude [deg]", ylabel="longitude [deg]")
plt.setp(ax_Height, xlabel="time [min]", ylabel="altitude [km]")

# gui
window = sg.Window("SAROMAN", __GUI.gui_layout, finalize=True)
gui_plot = __GUI.draw_figure(window["PLOT-OUT"].TKCanvas, p)

# save all the time stamps
complete_time_list: list[float] = []


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN LOOP
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

while True:
    gui_event, gui_values = window.read()
    if gui_event == "Exit" or gui_event == sg.WIN_CLOSED:
        break

    elif gui_event == "BTN-PLOT":
        try:
            # generate input data
            __INPUTS.TLE[0] = gui_values["TLE-LINE1"]
            __INPUTS.TLE[1] = gui_values["TLE-LINE2"]

            time_start = gui_values["DATE-START-OUT"] + "T" + gui_values["TIME-START-HR"] + ":" + gui_values["TIME-START-MIN"] + ":00"
            time_end = gui_values["DATE-END-OUT"] + "T" + gui_values["TIME-END-HR"] + ":" + gui_values["TIME-END-MIN"] + ":00"
            time_increment = 1/24 * float(gui_values["TIME-INCR-HR"]) + 1/(24 * 60) * float(gui_values["TIME-INCR-MIN"])

            __INPUTS.TIME_START = aTime(time_start).to_value('jd', 'float')
            __INPUTS.TIME_END = aTime(time_end).to_value('jd', 'float')
            __INPUTS.TIME_INCREMENT = time_increment

            # check time inputs
            if __INPUTS.TIME_END <= __INPUTS.TIME_START:
                raise Exception(f"Check Time Inputs!")
            if __INPUTS.TIME_INCREMENT > __INPUTS.TIME_END - __INPUTS.TIME_START:
                raise Exception(f"Time Increment is too big!")
            if __INPUTS.TIME_INCREMENT <= 0:
                raise Exception(f"Time Increment is smaller than or equal to 0!")

            # output the input data
            setup_info_string = f"SETUP INFO:\n\nTLE,L1: {__INPUTS.TLE[0]}\nTLE,L2: {__INPUTS.TLE[1]}\n\nStart Time: {time_start}\nEnd Time: {time_end}\nTime Increment: {time_increment} days"
            window["SETUP-DATA-OUT"].update(setup_info_string)
        except Exception as exc:
            # catch errors
            sg.popup_error(f"There seems to be an error with your input data: \n{exc}")
            continue    # jump to the next while-loop iteration

        try:
            # draw with color or in b/w
            check_colors = gui_values["CHECK-COLORS"]
            # generate satellite position data; additionally generates a list of colors for the plot
            list_lat, list_lon, list_segColors, list_height, list_times = __FUNCTIONS.GenerateGeodetics(check_colors=check_colors)

            for time in list_times:
                complete_time_list.append(time)
        except Exception as exc:
            # catch errors
            sg.popup_error(f"An error occured while calculating: \n{exc}")
            continue

        try:
            # split up the position data and draw the data onto the map
            draw_arrows = gui_values["CHECK-ARROW"]
            __FUNCTIONS.Split_and_Draw(list_lat=list_lat, list_lon=list_lon, ax=ax_Map, list_segColors=list_segColors, draw_arrows=draw_arrows)
            plt.setp(ax_Map, xticks=numpy.arange(start=-180, stop=181, step=30), yticks=numpy.arange(start=-90, stop=91, step=15), xlabel="latitude [deg]", ylabel="longitude [deg]")
            # format and plot height data
            min_time, max_time, time_stepsize, xlabels = __FUNCTIONS.draw_Height_Map(list_height=list_height, list_times=list_times, list_segColors=list_segColors, ax_Height=ax_Height, complete_time_list=complete_time_list)
            plt.setp(ax_Height, xticks=numpy.arange(start=min_time, stop=max_time, step=time_stepsize), xticklabels=xlabels, xlabel="time [min]", ylabel="altitude [km]")
            # draw plot to gui element
            plot_title = gui_values["TITLE"]
            plt.suptitle(plot_title)
            gui_plot.draw()
        except Exception as exc:
            # catch errors
            sg.popup_error(f"An error occured while graphing: \n{exc}")
            continue

    elif gui_event == "BTN-CLEAR":
        # reset the graph
        ax_Map.cla()
        ax_Height.cla()
        ax_Map.imshow(img, extent=[-180, 180, -90, 90])
        plt.setp(ax_Map, xticks=numpy.arange(start=-180, stop=181, step=30), yticks=numpy.arange(start=-90, stop=91, step=15), xlabel="latitude [deg]", ylabel="longitude [deg]")
        plt.setp(ax_Height, xlabel="time [min]", ylabel="altitude [km]")
        plt.title(label="")
        gui_plot.draw()
        # reset complete time list
        complete_time_list.clear()

    elif gui_event == "BTN-SAVE":
        # export the final image and show it on screen
        default_filename = gui_values["TITLE"]
        exportpath = SaveFileDialog(filetypes=[("Image", "*.png")], defaultextension="*.png", initialfile=default_filename)
        if exportpath != "":
            plt.savefig(exportpath, dpi=__SETTINGS.PLOT_DPI)

    elif gui_event == "BTN-COLOR":
        # open color chooser and write to input variables
        inputColor, hex = ColorChooser(color="#000000")
        __INPUTS.PLOT_COLOR = (inputColor[0]/255, inputColor[1]/255, inputColor[2]/255)
        window["TEXT-COLOR"].update(hex)

window.close()
