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
from . import wg

def rt_test_ring(radius=150, gap=0.2, wg_width=0.8, ring_width1=1, ring_width2=2, length=4900):

    D = Device()

    bd1 = D << wg.bd(radius=radius, angle=180, width=ring_width1, layer=ly.layer_ring)
    bd1.rotate(90)
    tp1 = D << wg.tp(width1=ring_width1, width2=ring_width2, length=200, layer=ly.layer_ring, width_type='sine')
    tp1.connect(port='o1', destination=bd1.ports['o2'])
    wg1 = D << wg.wg(width=ring_width2, length=length, layer=ly.layer_ring)
    wg1.connect(port='o1', destination=tp1.ports['o2'])
    tp1 = D << wg.tp(width1=ring_width2, width2=ring_width1, length=200, layer=ly.layer_ring, width_type='sine')
    tp1.connect(port='o1', destination=wg1.ports['o2'])
    bd1 = D << wg.bd(radius=radius, angle=180, width=ring_width1, layer=ly.layer_ring)
    bd1.connect(port='o1', destination=tp1.ports['o2'])
    tp1 = D << wg.tp(width1=ring_width1, width2=ring_width2, length=200, layer=ly.layer_ring, width_type='sine')
    tp1.connect(port='o1', destination=bd1.ports['o2'])
    wg1 = D << wg.wg(width=ring_width2, length=length, layer=ly.layer_ring)
    wg1.connect(port='o1', destination=tp1.ports['o2'])
    tp1 = D << wg.tp(width1=ring_width2, width2=ring_width1, length=200, layer=ly.layer_ring, width_type='sine')
    tp1.connect(port='o1', destination=wg1.ports['o2'])

    D.ymax = 0

    wg1 = D << wg.wg(width=wg_width, length=radius*2, layer=ly.layer_wg)
    wg1.move((-radius*2, wg_width/2+gap))
    D.add_port(name="o1", port=wg1.ports['o1'])
    D.add_port(name="o2", port=wg1.ports['o2'])

    txt = D << pg.text(text='radius={radius}, gap={gap}, wg_width={wg_width}, ring_width1={ring_width1}, ring_width2={ring_width2}, length={length}'.format(radius=radius, gap=gap, wg_width=wg_width, ring_width1=ring_width1, ring_width2=ring_width2, length=length), 
                       size=20, layer=ly.layer_label)
    txt.rotate(-90).move((-radius, -radius*2))
    return D