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
from zjlab_ln.layers import ly

WG_WIDTH = 0.8
MOD_WG_WIDTH = 2
MOD_PITCH = 58.2

# straight waveguide
def wg(width=WG_WIDTH, length=500, layer=ly.layer_wg):

    D = Device()

    P = Path()
    P.append( pp.straight(length = length) )
    D = P.extrude([width,width], layer = layer)

    # endpoints from the path
    start_pt = P.points[0]     # (x, y) at start
    end_pt   = P.points[-1]    # (x, y) at end

    # add ports
    D.add_port(name="o1", midpoint=tuple(start_pt), width=width, orientation=180)
    D.add_port(name="o2", midpoint=tuple(end_pt),   width=width, orientation=0)

    return D

# tapered waveguide, width_type = 'sine' or 'linear'
def tp(width1=WG_WIDTH, width2=MOD_WG_WIDTH, length=200, layer=ly.layer_wg, width_type='sine'):

    D = Device()

    X1 = CrossSection()
    X1.add(width = width1, offset = 0, layer = layer, name = 'wg1')
    X2 = CrossSection()
    X2.add(width = width2, offset = 0, layer = layer, name = 'wg1')

    Xtrans = pp.transition(cross_section1 = X1,
                        cross_section2 = X2,
                        width_type = width_type)
    
    P = Path().append(pp.straight(length = length))
    D = P.extrude(Xtrans)

    # endpoints from the path
    start_pt = P.points[0]     # (x, y) at start
    end_pt   = P.points[-1]    # (x, y) at end

    # add ports
    D.add_port(name="o1", midpoint=tuple(start_pt), width=width1, orientation=180)
    D.add_port(name="o2", midpoint=tuple(end_pt),   width=width2, orientation=0)

    return D

# bending waveguide
def bd(radius=50, angle=90, width=WG_WIDTH, layer=ly.layer_wg):

    P = Path()
    P.append(pp.euler(radius=radius, angle=angle, use_eff=True))
    D = P.extrude(width=width, layer=layer)   # constant-width extrude

    # endpoints from the path
    start_pt = P.points[0]     # (x, y) at start
    end_pt   = P.points[-1]    # (x, y) at end

    # add ports
    D.add_port(name="o1", midpoint=tuple(start_pt), width=width, orientation=180)
    D.add_port(name="o2", midpoint=tuple(end_pt),   width=width, orientation=angle)

    return D


# s-bending waveguide
def sbd(length=1000, offset=100, width=WG_WIDTH, layer=ly.layer_wg):

    D = Device()

    X1 = CrossSection()
    X1.add(width = width, offset = 0, layer = layer, name = 'wg1')
    X2 = CrossSection()
    X2.add(width = width, offset = -offset, layer = layer, name = 'wg1')

    Xtrans = pp.transition(cross_section1 = X1, cross_section2 = X2, width_type = 'linear')
    
    P = Path().append(pp.straight(length = length))
    D = P.extrude(Xtrans)

    # endpoints from the path
    start_pt = P.points[0]     # (x, y) at start
    end_pt   = P.points[-1]    # (x, y) at end
    end_pt[1] += offset

    # add ports
    D.add_port(name="o1", midpoint=tuple(start_pt), width=width, orientation=180)
    D.add_port(name="o2", midpoint=tuple(end_pt),   width=width, orientation=0)

    return D

# Y splitters
def ysp(width=WG_WIDTH, length=400, pitch=MOD_PITCH, layer=ly.layer_wg, width_type='sine'):

    D = Device()

    tp1 = D << tp(width1=width, width2=width * 2, length=length/2, layer=layer, width_type=width_type)
    sbd1 = D << sbd(length=length/2, offset=(pitch/2)-width/2, width=width, layer=layer)
    sbd1.move((length/2,width/2))
    sbd2 = D << sbd(length=length/2, offset=-(pitch/2)+width/2, width=width, layer=layer)
    sbd2.move((length/2,-width/2))

    D.add_port(name="o1", port=tp1.ports["o1"])
    D.add_port(name="o2", port=sbd1.ports["o2"])
    D.add_port(name="o3", port=sbd2.ports["o2"])

    return D

# directional coupler 50:50
def dc(width=WG_WIDTH, length=63.3, gap=1, layer=ly.layer_wg):

    D = Device()

    straight1 = D << wg(width=width, length=length, layer=layer)
    straight2 = D << wg(width=width, length=length, layer=layer)
    straight2.move((0, -width-gap))

    sbd1 = D << sbd(length=200, offset=-(MOD_PITCH/2-(width+gap)/2), width=width, layer=layer)
    sbd1.connect("o1", straight1.ports["o1"])
    D.add_port(name="o1", port=sbd1.ports["o2"])
    sbd2 = D << sbd(length=200, offset=(MOD_PITCH/2-(width+gap)/2), width=width, layer=layer)
    sbd2.connect("o1", straight1.ports["o2"])
    D.add_port(name="o2", port=sbd2.ports["o2"])
    sbd3 = D << sbd(length=200, offset=-(MOD_PITCH/2-(width+gap)/2), width=width, layer=layer)
    sbd3.connect("o1", straight2.ports["o2"])
    D.add_port(name="o3", port=sbd3.ports["o2"])
    sbd4 = D << sbd(length=200, offset=(MOD_PITCH/2-(width+gap)/2), width=width, layer=layer)
    sbd4.connect("o1", straight2.ports["o1"])
    D.add_port(name="o4", port=sbd4.ports["o2"])

    txt = D << pg.text(text="len_width_gap: "+str(length)+" "+str(width)+" "+str(gap), size=10, layer=ly.layer_label)
    txt.move((-50, -50))

    return D

def wg_cross():
    D = Device()
    tp1 = D << tp(length=4, width1=0.8, width2=2.4, layer=ly.layer_wg)
    wg1 = D << wg(width=2.4, layer = ly.layer_wg, length=14)
    wg1.connect('o1', destination=tp1.ports['o2'])
    tp2 = D << tp(length=4, width1=2.4, width2=0.8, layer=ly.layer_wg)
    tp2.connect('o1', destination=wg1.ports['o2'])

    tp3 = D << tp(length=4, width1=0.8, width2=2.4, layer=ly.layer_wg)
    tp3.rotate(-90).move([11,11])
    wg2 = D << wg(width=2.4, layer = ly.layer_wg, length=14)
    wg2.connect('o1', destination=tp3.ports['o2'])
    tp4 = D << tp(length=4, width1=2.4, width2=0.8, layer=ly.layer_wg)
    tp4.connect('o1', destination=wg2.ports['o2'])

    D.add_port(name='o1', port=tp1.ports['o1'])
    D.add_port(name='o2', port=tp3.ports['o1'])
    D.add_port(name='o3', port=tp2.ports['o1'])
    D.add_port(name='o4', port=tp4.ports['o1'])

    return D