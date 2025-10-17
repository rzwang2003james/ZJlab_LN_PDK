from turtle import width
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
from zjlab_ln.layers import ly

M_ROUTE_WIDTH = 50
AU_PAD = 100

# straight metal
def mt(width=M_ROUTE_WIDTH, length=500, layer=ly.layer_metal):

    D = Device()

    P = Path()
    P.append( pp.straight(length = length) )
    D = P.extrude([width,width], layer = layer)

    # endpoints from the path
    start_pt = P.points[0]     # (x, y) at start
    end_pt   = P.points[-1]    # (x, y) at end

    # add ports
    D.add_port(name="e1", midpoint=tuple(start_pt), width=width, orientation=180)
    D.add_port(name="e2", midpoint=tuple(end_pt),   width=width, orientation=0)

    return D

# metal pads
def rd_pad(size=(AU_PAD, AU_PAD), corner_radi=5,layer=ly.layer_metal):
    D = Device()
    rect = pg.rectangle(size=size, layer=layer)
    rounded = pg.offset(
        rect,
        distance=corner_radi, 
        join='round', 
        layer=layer,
        tolerance=0.01
    )

    D << rounded
    D.add_port(name='e1', midpoint=(0, size[1]/2), width=size[1]+2*corner_radi, orientation=180)
    D.add_port(name='e2', midpoint=(size[0]/2, size[1]), width=size[1]+2*corner_radi, orientation=90)
    D.add_port(name='e3', midpoint=(size[0], size[1]/2), width=size[1]+2*corner_radi, orientation=0)
    D.add_port(name='e4', midpoint=(size[0]/2, 0), width=size[1]+2*corner_radi, orientation=-90)

    return D

# metal linear taper for transitions
def mt_linear_trans(width1=5, width2=10, length=500, offset=10, layer=ly.layer_metal):

    D = Device()

    c1 = D << pg.compass(size=(0, width1), layer=layer)
    c2 = D << pg.compass(size=(0, width2), layer=layer).move([length,offset])
    
    D.add_port(name='e1', port=c1.ports['W'])
    D.add_port(name='e2', port=c2.ports['E'])

    R = D << pr.route_quad(c1.ports['E'], c2.ports['W'],
                    width1 = None, width2 = None,
                    layer = layer)

    return D

# metal sine taper for transitions
def mt_sine_trans(width1=5, width2=10, length=500, offset=10, layer=ly.layer_metal):

    D = Device()

    X1 = CrossSection()
    X1.add(width = width1, offset = 0, layer = layer, name = 'mt1')
    X2 = CrossSection()
    X2.add(width = width2, offset = -offset, layer = layer, name = 'mt1')

    Xtrans = pp.transition(cross_section1 = X1,
                        cross_section2 = X2,
                        width_type = 'sine')
    
    P = Path().append(pp.straight(length = length))
    D = P.extrude(Xtrans)

    # endpoints from the path
    start_pt = P.points[0]     # (x, y) at start
    end_pt   = P.points[-1]    # (x, y) at end
    end_pt[1] += offset

    # add ports
    D.add_port(name="e1", midpoint=tuple(start_pt), width=width1, orientation=180)
    D.add_port(name="e2", midpoint=tuple(end_pt),   width=width2, orientation=0)

    return D

def seg_wg_high_speed(wg_width = wg.MOD_WG_WIDTH, ele_width1 = 50, ele_width2 = 50, length = 1000, gap=3.7, ele_gap = 18.2):

    D = Device()
    
    wg1 = D << wg.wg(width=wg_width, layer = ly.layer_wg, length=length)
    wgin = D << wg.tp(width1=wg.WG_WIDTH, width2=wg_width, layer = ly.layer_wg, length=200)
    wgin.connect(port='o2', destination=wg1.ports['o1'])
    wgout = D << wg.tp(width1=wg_width, width2=wg.WG_WIDTH, layer = ly.layer_wg, length=200)
    wgout.connect(port='o1', destination=wg1.ports['o2'])
    D.add_port(name = "o1", port=wgin.ports['o1'])
    D.add_port(name = "o2", port=wgout.ports['o2'])

    t_width = 1
    t_length = 45
    t_pitch = 50

    ele1 = D << mt(width=ele_width1, length=length, layer=ly.layer_metal)
    ele1.move((0, ele_gap/2+ele_width1/2))
    D.add_port(name = "e1", port=ele1.ports['e1'])
    D.add_port(name = "e2", port=ele1.ports['e2'])
    ele2 = D << mt(width=ele_width2, length=length, layer=ly.layer_metal)
    ele2.move((0, -ele_gap/2-ele_width2/2))
    D.add_port(name = "e3", port=ele2.ports['e2'])
    D.add_port(name = "e4", port=ele2.ports['e1'])

    i = 0
    while i < (length / t_pitch):
        mt1 = D << mt(width=1, length=t_length, layer=ly.layer_metal)
        mt1.move((t_pitch*i,gap/2+t_width/2))
        vmt1 = D << mt(width=1, length=(ele_gap-gap)/2, layer=ly.layer_metal)
        vmt1.rotate(90).move((t_length/2+t_pitch*i,gap/2))

        mt2 = D << mt(width=1, length=t_length, layer=ly.layer_metal)
        mt2.move((t_pitch*i,-gap/2-t_width/2))
        vmt2 = D << mt(width=1, length=(ele_gap-gap)/2, layer=ly.layer_metal)
        vmt2.rotate(-90).move((t_length/2+t_pitch*i,-gap/2))

        i += 1

    return D

def seg_wg_low_speed(wg_width = wg.MOD_WG_WIDTH, ele_width1 = 50, ele_width2 = 50, length = 1000, gap=3.7):

    D = Device()

    wg1 = D << wg.wg(width=wg_width, layer = ly.layer_wg, length=length)
    wgin = D << wg.tp(width1=wg.WG_WIDTH, width2=wg_width, layer = ly.layer_wg, length=200)
    wgin.connect(port='o2', destination=wg1.ports['o1'])
    wgout = D << wg.tp(width1=wg_width, width2=wg.WG_WIDTH, layer = ly.layer_wg, length=200)
    wgout.connect(port='o1', destination=wg1.ports['o2'])
    D.add_port(name = "o1", port=wgin.ports['o1'])
    D.add_port(name = "o2", port=wgout.ports['o2'])

    ele1 = D << mt(width=ele_width1, length=length, layer=ly.layer_metal)
    ele1.move((0, gap/2+ele_width1/2))
    D.add_port(name = "e1", port=ele1.ports['e1'])
    D.add_port(name = "e2", port=ele1.ports['e2'])

    ele2 = D << mt(width=ele_width2, length=length, layer=ly.layer_metal)
    ele2.move((0, -gap/2-ele_width2/2))
    D.add_port(name = "e3", port=ele2.ports['e2'])
    D.add_port(name = "e4", port=ele2.ports['e1'])

    return D

def gsg_seg_wg(wg_width = wg.MOD_WG_WIDTH, g_width = 130, s_width = 40, length = 1000, gap=3.7, ele_gap = 18.2, high_speed=True, termination=True):

    D = Device()

    if high_speed:
        seg_wg1 = D << seg_wg_high_speed(wg_width=wg_width, ele_width1=g_width, ele_width2=s_width, length=length, gap=gap, ele_gap=ele_gap)
        seg_wg2 = D << seg_wg_high_speed(wg_width=wg_width, ele_width1=s_width, ele_width2=g_width, length=length, gap=gap, ele_gap=ele_gap)
        seg_wg2.move((0, -s_width - ele_gap))
        if termination:
            ter = D << gsg_termination(g_width1 = g_width, s_width1 = s_width, gap1=14, g_width2 = 150, s_width2 = 240, gap2=180, length = 155)
            ter.connect(port='e1', destination=seg_wg2.ports['e2'])
    else:
        seg_wg1 = D << seg_wg_low_speed(wg_width=wg_width, ele_width1=g_width, ele_width2=s_width, length=length, gap=gap)
        seg_wg2 = D << seg_wg_low_speed(wg_width=wg_width, ele_width1=s_width, ele_width2=g_width, length=length, gap=gap)
        seg_wg2.move((0, -s_width - ele_gap))

    D.add_port(name="o1", port=seg_wg1.ports['o1'])
    D.add_port(name="o2", port=seg_wg1.ports['o2'])

    D.add_port(name="o3", port=seg_wg2.ports['o2'])
    D.add_port(name="o4", port=seg_wg2.ports['o1'])

    D.add_port(name="se1", port=seg_wg1.ports['e4'])
    D.add_port(name="se2", port=seg_wg2.ports['e2'])

    return D

def gsg_linear_taper(g_width1 = 130, s_width1 = 40, gap1=14, g_width2 = 150, s_width2 = 100, gap2=43, length = 35):

    D = Device()

    os = (g_width2 - g_width1)/2 + gap2 - gap1 + (s_width2 - s_width1)/2

    taper1 = D << mt_linear_trans(width1=g_width1, width2=g_width2, length=length, offset=os, layer=ly.layer_metal)
    taper1.move((0, s_width1/2+gap1+g_width1/2))

    taper2 = D << mt_linear_trans(width1=s_width1, width2=s_width2, length=length, offset=0, layer=ly.layer_metal)

    taper3 = D << mt_linear_trans(width1=g_width1, width2=g_width2, length=length, offset=-os, layer=ly.layer_metal)
    taper3.move((0, -s_width1/2-gap1-g_width1/2))

    D.add_port(name="se1", port=taper2.ports['e1'])
    D.add_port(name="se2", port=taper2.ports['e2'])

    D.add_port(name="ge1", port=taper1.ports['e2'])
    D.add_port(name="ge2", port=taper3.ports['e2'])

    return D

def gsg_termination(g_width1 = 130, s_width1 = 40, gap1=14, g_width2 = 150, s_width2 = 240, gap2=180, length = 155):

    D = Device()

    ht_length = gap2 * 2 + s_width2 + 2 * g_width2
    ht_width = 10

    taper1 = D << gsg_linear_taper(g_width1=g_width1, s_width1=s_width1, gap1=gap1, g_width2=g_width2, s_width2=s_width2, gap2=gap2, length=length)
    ht = D << mt(width=ht_width, length=ht_length, layer=ly.layer_heater)
    ht.rotate(90).move((length+ht_width/2, -ht_length/2))

    g1 = D << pg.compass(size=(g_width2, ht_width), layer=ly.layer_metal)
    g1.connect(port='N', destination=taper1.ports['ge1'])
    s1 = D << pg.compass(size=(s_width2, ht_width), layer=ly.layer_metal)
    s1.connect(port='N', destination=taper1.ports['se2'])
    g2 = D << pg.compass(size=(g_width2, ht_width), layer=ly.layer_metal)
    g2.connect(port='N', destination=taper1.ports['ge2'])

    D.add_port(name="e1", port=taper1.ports['se1'])

    return D