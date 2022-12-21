# FUNCTIONS
import astropy.coordinates
# library imports
import numpy

from sgp4.api import Satrec
from sgp4.api import SGP4_ERRORS

from astropy.coordinates import TEME, CartesianDifferential, CartesianRepresentation, ITRS
from astropy import units
from astropy.time import Time

# import of own functions and variables
import settings as __SETTINGS
import inputs as __INPUTS


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# generate list of geodetic coordinates of satellite positions; generates a list of colors, that are used to color the plot
def GenerateGeodetics(check_colors):
    list_teme: list[astropy.coordinates.TEME()] = []
    list_lon: list[float] = []
    list_lat: list[float] = []
    list_height: list[float] = []
    list_times: list[float] = []

    calc_time = __INPUTS.TIME_START
    while calc_time <= __INPUTS.TIME_END:       # time loop
        calc_time += __INPUTS.TIME_INCREMENT
        t = Time(calc_time, format='jd')

        teme = Get_TEME(time=t)
        itrs = TEME_to_ITRS(time=t, teme=teme)
        gcs_lat, gcs_lon, gcs_height = ITRS_to_GEODETIC(itrs)

        list_teme.append(teme)
        list_lat.append(gcs_lat)
        list_lon.append(gcs_lon)
        list_height.append(gcs_height)
        list_times.append(calc_time)

    list_segColors = Calc_Colors(list_teme=list_teme, check_colors=check_colors)

    return list_lat, list_lon, list_segColors, list_height, list_times


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# get satellite data in TEME reference frame for a specific point in time
def Get_TEME(time):
    tle_satrec = Satrec.twoline2rv(__INPUTS.TLE[0], __INPUTS.TLE[1])
    error_code, teme_position, teme_velocity = tle_satrec.sgp4(time.jd1, time.jd2)

    if error_code != 0:
        raise RuntimeError(SGP4_ERRORS[error_code])

    teme_position = CartesianRepresentation(teme_position * units.km)  # setup TEME to use SI units
    teme_velocity = CartesianDifferential(teme_velocity * units.km / units.s)

    teme = TEME(teme_position.with_differentials(teme_velocity), obstime=time)

    return teme


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# transform satellite data from TEME to ITRS reference frame for a specific point in time
def TEME_to_ITRS(time, teme):
    itrs_base = teme.transform_to(ITRS(obstime=time))
    itrs_earth = itrs_base.earth_location

    return itrs_earth


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# transform satellite data from ITRS to geodetic coordinates
def ITRS_to_GEODETIC(itrs):
    geod_lat = itrs.geodetic.lat.degree
    geod_lon = itrs.geodetic.lon.degree
    geod_height = itrs.height.value

    return geod_lat, geod_lon, geod_height


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# calculate distances between points and generate rgb color values
def Calc_Colors(list_teme, check_colors):
    list_pointDist: list[float] = []
    list_segColors: list[(float, float, float)] = []

    for i in range(len(list_teme) - 1):
        list_pointDist.append(float(numpy.sqrt(numpy.power(list_teme[i + 1].x.value - list_teme[i].x.value, 2) + numpy.power(list_teme[i + 1].y.value - list_teme[i].y.value, 2) + numpy.power(list_teme[i + 1].z.value - list_teme[i].z.value, 2))))

    dist_min = min(list_pointDist)
    dist_max = max(list_pointDist)

    for dist in list_pointDist:
        r = 1
        g = (dist - dist_min) * 1 / (dist_max - dist_min)
        b = 0
        if check_colors:
            list_segColors.append((r, g, b))
        else:
            list_segColors.append(__INPUTS.PLOT_COLOR)

    return list_segColors


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# split up the position data and draw the data onto the map
def Split_and_Draw(list_lat, list_lon, ax, list_segColors, draw_arrows):
    subList_lat: list[float] = []
    subList_lon: list[float] = []
    subList_segColors: list[(float, float, float, float)] = []

    last_overflow = 0
    for i in range(len(list_lat) - 1):
        if numpy.abs(list_lon[i] - list_lon[i + 1]) > __SETTINGS.LONGITUDE_JUMP_CUTOFF:
            # generate sublists, which are not interrupted by a "map overflow"
            for j in range(last_overflow, i+1):
                subList_lat.append(list_lat[j])
                subList_lon.append(list_lon[j])
                subList_segColors.append(list_segColors[j])
            # interpolate, so that the lines are drawn right to the edge of the plot, if a cutoff happens immediately after
            interp_lat = 0
            if list_lon[i + 1] < 0:
                point_projected_lon = list_lon[i + 1] + 360
                point_projected_lat = list_lat[i + 1]
                # cal m(x - c) + b
                b = list_lat[i]
                c = list_lon[i]
                m = (point_projected_lat - list_lat[i]) / (point_projected_lon - list_lon[i])
                # interpolate for x = 180deg
                interp_lat = m * (180 - c) + b
                interp_lon = 180
                subList_lat.append(interp_lat)
                subList_lon.append(interp_lon)
                subList_segColors.append(list_segColors[i])
            if list_lon[i + 1] > 0:
                point_projected_lon = list_lon[i + 1] - 360
                point_projected_lat = list_lat[i + 1]
                # cal m(x - c) + b
                b = list_lat[i]
                c = list_lon[i]
                m = (point_projected_lat - list_lat[i]) / (point_projected_lon - list_lon[i])
                # interpolate for x = -180deg
                interp_lat = m * (-180 - c) + b
                interp_lon = -180
                subList_lat.append(interp_lat)
                subList_lon.append(interp_lon)
                subList_segColors.append(list_segColors[i])
            # plot the sublists pair by pair, to apply a different color to every segment (depending on the speed of the satellite)
            for k in range(len(subList_lat) - 1):
                twoPoints_lat = [subList_lat[k], subList_lat[k + 1]]
                twoPoints_lon = [subList_lon[k], subList_lon[k + 1]]
                ax.plot(twoPoints_lon, twoPoints_lat, linewidth=1, color=subList_segColors[k])
            if draw_arrows:
                add_Arrow(ax, subList_lon, subList_lat, subList_segColors)
            last_overflow = i + 1
            subList_lat.clear()
            subList_lon.clear()
            subList_segColors.clear()
            # interpolate, so that entering lines are drawn right to the edge of the plot, if a cutoff happened right before
            # uses the calculated interpolated latitudes from above
            if list_lon[i] > 0:
                interp_lon = -180
                subList_lat.append(interp_lat)
                subList_lon.append(interp_lon)
                subList_segColors.append(list_segColors[i])
            if list_lon[i] < 0:
                interp_lon = 180
                subList_lat.append(interp_lat)
                subList_lon.append(interp_lon)
                subList_segColors.append(list_segColors[i])

    for j in range(last_overflow, len(list_lat)):
        subList_lat.append(list_lat[j])
        subList_lon.append(list_lon[j])
        if j < len(list_segColors):
            subList_segColors.append(list_segColors[j])
    for k in range(len(subList_lat) - 1):
        twoPoints_lat = [subList_lat[k], subList_lat[k + 1]]
        twoPoints_lon = [subList_lon[k], subList_lon[k + 1]]
        ax.plot(twoPoints_lon, twoPoints_lat, linewidth=1, color=subList_segColors[k])
    if draw_arrows:
        add_Arrow(ax, subList_lon, subList_lat, subList_segColors)

    return ax


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# draw height map
def draw_Height_Map(list_times, list_height, complete_time_list, list_segColors, ax_Height):
    for i in range(len(list_times) - 1):
        times = [list_times[i], list_times[i + 1]]
        heights = [list_height[i], list_height[i + 1]]
        segColor = list_segColors[i]
        ax_Height.plot(times, heights, linewidth=1, color=segColor)

    min_time = min(complete_time_list)
    max_time = max(complete_time_list)
    time_stepsize = (max_time - min_time) / __SETTINGS.HEIGHT_PLOT_TIME_STEPS

    min_time_label = 0
    max_time_label = (max_time - min_time) * 24 * 60
    time_stepsize_label = time_stepsize * 24 * 60

    xlabels: list[str] = []
    for time in numpy.arange(start=min_time_label, stop=max_time_label, step=time_stepsize_label):
        xlabels.append(str(numpy.round(time, 0)))

    if len(xlabels) < len(numpy.arange(start=min_time, stop=max_time, step=time_stepsize)):
        for i in range(len(numpy.arange(start=min_time, stop=max_time, step=time_stepsize)) - len(xlabels)):
            xlabels.append(str(numpy.round(max_time_label, 0)))
    elif len(xlabels) > len(numpy.arange(start=min_time, stop=max_time, step=time_stepsize)):
        for i in range(len(xlabels) - len(numpy.arange(start=min_time, stop=max_time, step=time_stepsize))):
            xlabels.pop()

    return min_time, max_time, time_stepsize, xlabels


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# creates an arrow in the middle of the line to indicate its direction
def add_Arrow(line, xdata, ydata, subList_segColors):
    if len(xdata) != 0:
        size = __SETTINGS.PLOT_ARROW_SIZE

        start_ind = numpy.argmin(numpy.absolute(xdata))     # find closest index

        if start_ind == len(xdata) - 1:
            end_ind = start_ind
            start_ind -= 1
        else:
            end_ind = start_ind + 1

        line.axes.annotate('', xytext=(xdata[start_ind], ydata[start_ind]), xy=(xdata[end_ind], ydata[end_ind]), arrowprops=dict(arrowstyle="->", color=subList_segColors[start_ind]), size=size)
