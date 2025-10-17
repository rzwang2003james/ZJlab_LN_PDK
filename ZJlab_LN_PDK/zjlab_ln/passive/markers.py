from phidl import quickplot as qp
import scipy.integrate as integrate
import phidl.geometry as pg
import sys
import os
from phidl import Device, Layer, LayerSet, device_layout, Path, CrossSection
import phidl.routing as pr
import phidl.utilities as pu
import phidl.path as pp
import numpy as np

from zjlab_ln.passive import rings, wg
from zjlab_ln.active import heater, mrm, mzm, metal
from zjlab_ln.layers import ly

def align1():
    D = Device()
    
    # Define positions and rotations for each caliper
    positions = [(0, 0), (-10, -95), (85, -105), (95, -10)]
    rotations = [0, 90, 180, -90]

    # Add calipers at specified positions and orientations
    for pos, rot in zip(positions, rotations):
        cali = D << pg.litho_calipers(
            notch_size=[1, 5],
            notch_spacing=5,
            num_notches=7,
            offset_per_notch=-0.1,
            row_spacing=0,
            layer1=ly.layer_Aligncheck,
            layer2=ly.layer_PM
        )
        cali.rotate(rot).move(pos)

    # Add a lithography step pattern and center the device
    step = D << pg.litho_steps(line_widths=[0.05, 0.1, 0.25, 0.5, 1, 2, 4, 8], line_spacing=5, height=30, layer=ly.layer_PM)
    step.move([20, -55])
    D.center = (0, 0)
    
    return D

def align2():
    D = Device()
    
    # Add a cross in the center of the device
    D << pg.cross(length=100, width=2, layer=ly.layer_PM)

    # Define the primary positions for XOR rectangles
    xor_positions = [(10, 10), (-34, 10), (10, -34), (-34, -34)]
    
    # Create XOR rectangles and position them
    for pos in xor_positions:
        sq1 = pg.rectangle(size=(24, 24), layer=ly.layer_PM)
        sq2 = pg.rectangle(size=(20, 20), layer=ly.layer_PM).move([2, 2])
        xm = D << pg.boolean(A=sq1, B=sq2, operation='xor', precision=1e-6, num_divisions=[1, 1], layer=ly.layer_PM)
        xm.move(pos)

    # Place inner test layer squares at adjusted positions
    for pos in xor_positions:
        sq = D << pg.rectangle(size=(16, 16), layer=ly.layer_Aligncheck)
        sq.move([pos[0] + 4, pos[1] + 4])

    # Define and place additional test layer squares at offsets
    additional_positions = [
        (10 + 22, 10 + 22),
        (-34 - 22, 10 + 22),
        (10 + 22, -34 - 22),
        (-34 - 22, -34 - 22)
    ]
    
    for pos in additional_positions:
        sq = D << pg.rectangle(size=(16, 16), layer=ly.layer_Aligncheck)
        sq.move([pos[0] + 4, pos[1] + 4])

    # Center the device for alignment
    D.center = (0, 0)
    
    return D

def markers(size=(1000, 1000)):
    D = Device()
    
    # Define positions for corners, XOR markers, small squares, and crosses
    corner_positions = [(0, 0), (size[0], 0), (0, size[1]), (size[0], size[1])]
    xm_positions = [(200, 0), (size[0] - 200, 0), (200, size[1]), (size[0] - 200, size[1])]
    sq_positions = [(0, -150), (size[0], -150), (0, size[1] + 150), (size[0], size[1] + 150)]
    cross_positions = [(200, -150), (size[0] - 200, -150), (200, size[1] + 150), (size[0] - 200, size[1] + 150)]
    deep_sq_positions = [(0, -450), (size[0], -450), (0, size[1] + 450), (size[0], size[1] + 450)]
    deep_cross_positions = [(200, -450), (size[0] - 200, -450), (200, size[1] + 450), (size[0] - 200, size[1] + 450)]

    # Place cross markers at each corner of the bounding area
    for pos in corner_positions:
        D << pg.cross(length=100, width=15, layer=ly.layer_PM).move(pos)

    # Place XOR markers with a cross pattern and offset rectangle for each position
    for pos in xm_positions:
        x = pg.cross(length=100, width=15, layer=ly.layer_PM)
        sq = pg.rectangle(size=(110, 110), layer=ly.layer_PM).move([-55, -55])
        xm = D << pg.boolean(A=x, B=sq, operation='xor', precision=1e-6, num_divisions=[1, 1], layer=ly.layer_PM)
        xm.move(pos)

    # Place small squares and deep squares at respective positions
    for pos in sq_positions + deep_sq_positions:
        sq = D << pg.rectangle(size=(20, 20), layer=ly.layer_PM).move([-10, -10])
        sq.move(pos)

    # Place small crosses at cross and deep cross positions
    for pos in cross_positions + deep_cross_positions:
        D << pg.cross(length=20, width=3, layer=ly.layer_PM).move(pos)

    # Place alignment marks at specific locations around the bounding area
    for align_pos in [(0, -300), (size[0], -300), (0, size[1] + 300), (size[0], size[1] + 300)]:
        D << align1().move(align_pos)

    # Place secondary alignment marks with offset locations
    for align_pos in [(200, -300), (size[0] - 200, -300), (200, size[1] + 300), (size[0] - 200, size[1] + 300)]:
        D << align2().move(align_pos)
    D.center = (0,0)
    return D