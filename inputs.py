# INPUT VARIABLES

# to be manipulated by the gui (user)

TLE = [str, str]              # both lines of the TLE, separated by ","

TIME_START: float             # start time for calculation, in jd-format
TIME_END: float               # end time for calculation, in jd-format
TIME_INCREMENT: float         # time increment for calculation, in jd-format

PLOT_COLOR: (float, float, float) = (0, 0, 0)