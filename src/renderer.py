import numpy as np
from numba import njit

@njit # Speed up with numba to increase FPS
def new_frame(x_pos, y_pos, rot, hres, harf_vres, mod, sky, cource, frame):
    for i in range(hres):
        i_rot = rot + np.deg2rad(i/mod-30)
        sin, cos = np.sin(i_rot), np.cos(i_rot)
        cos2 = np.cos(np.deg2rad(i/mod-30))
        index = int(np.rad2deg(i_rot)%360)
        if index >= 360:
            index = 359
        frame[i][:] = sky[index][:]/255

        for j in range(harf_vres):
            n = (harf_vres/(harf_vres-j))/cos2
            x, y = x_pos + n*cos, y_pos + n*sin
            xx, yy = int(x/20%1*200), int(y/20%1*200)
            frame[i][harf_vres*2-j-1] = cource[xx][yy]/255

    return frame
