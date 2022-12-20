# GUI SETUP

# library imports
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg

gui_setup = [
    [
        sg.Text("SAROMAN", size=(60, 1), font=("Arial", 16, " underline")),
    ],
    [
        sg.Text("SAtellite Route and Orbit MAppiNg tool"),
    ],
    [
        sg.Text("", size=(1, 6)),
    ],
    # title
    [
        sg.Text("Diagram title:", size=(10, 1)),
        sg.In(enable_events=True, key="TITLE", size=(40, 1)),
    ],
    # TLE
    [
        sg.Text("TLE, Line 1:", size=(10, 1)),
        sg.In(enable_events=True, key="TLE-LINE1", size=(65,1)),
    ],
    [
        sg.Text("TLE, Line 2:", size=(10, 1)),
        sg.In(enable_events=True, key="TLE-LINE2", size=(65,1)),
    ],
    # TIME
    [
        sg.Text("Time (Start):", size=(10, 1)),
        sg.CalendarButton(target = "DATE-START-OUT", enable_events=True, key="CALENDAR-START", button_text="Date", format = "%Y-%m-%d"),
        sg.In(size=(10, 1),  key="DATE-START-OUT", enable_events=True, disabled=True),
        sg.Text("hr:"),
        sg.In(size=(5, 1), enable_events=True, key="TIME-START-HR"),
        sg.Text("min:"),
        sg.In(size=(5, 1), enable_events=True, key="TIME-START-MIN"),
    ],
    [
        sg.Text("Time (End):", size=(10, 1)),
        sg.CalendarButton(target = "DATE-END-OUT", enable_events=True, key="CALENDAR-END", button_text="Date", format = "%Y-%m-%d"),
        sg.In(size=(10, 1), key="DATE-END-OUT", enable_events=True, disabled=True),
        sg.Text("hr:"),
        sg.In(size=(5, 1), enable_events=True, key="TIME-END-HR"),
        sg.Text("min:"),
        sg.In(size=(5, 1), enable_events=True, key="TIME-END-MIN"),
    ],
    [
        sg.Text("Increment:", size=(10, 1)),
        sg.Text("hr:"),
        sg.In(size=(5, 1), enable_events=True, key="TIME-INCR-HR"),
        sg.Text("min:"),
        sg.In(size=(5, 1), enable_events=True, key="TIME-INCR-MIN"),
    ],
    # PLOT BTN and SETUP DATA
    [
        sg.CBox(enable_events=True, text="plot velocity as line color", key="CHECK-COLORS", size=(25,1)),
        sg.Button(button_text="Plot", size=(15, 1), enable_events=True, key="BTN-PLOT"),
        sg.Button(button_text="Color", size=(10,1), enable_events=True ,key="BTN-COLOR"),
        sg.Text(enable_events=True, text="#000000", key="TEXT-COLOR"),
    ],
    [
        sg.CBox(enable_events=True, text="plot flight direction", key="CHECK-ARROW", size=(25,1)),
        sg.Button(button_text="Clear", size=(15, 1), enable_events=True, key="BTN-CLEAR"),
        sg.Button(button_text="Save Image", size=(10, 1), enable_events=True, key="BTN-SAVE"),
    ],
    [
        sg.Text(size=(80, 15), key="SETUP-DATA-OUT"),
    ],
]

gui_image = [
    [
        sg.Canvas(key="PLOT-OUT"),
    ],
]

gui_layout = [
    [
        sg.Column(gui_setup),
        sg.VSeparator(),
        sg.Column(gui_image),
    ]
]

def draw_figure(canvas, figure):
    matplotlib.use("TkAgg")
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=0)
    figure_canvas_agg.get_tk_widget().place()
    return figure_canvas_agg
