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
from . import metal

# Heaters with integrated waveguides
def heater_str(length=500, width=7, to_wg=0):

    D = Device()

    # Create the waveguide
    wg1 = D << wg.wg(length=length, width=wg.WG_WIDTH, layer=ly.layer_wg)
    D.add_port(name='o1', port=wg1.ports['o1'])
    D.add_port(name='o2', port=wg1.ports['o2'])

    # Create the heater element
    heater = D << pg.compass(size=(length, width), layer=ly.layer_heater)
    heater.move((length/2, -to_wg))

    # Add heater pads
    pad_size = metal.M_ROUTE_WIDTH + 10

    trans1 = D << metal.mt_sine_trans(width1=width, width2=pad_size+10, length=pad_size*2, offset=pad_size, layer=ly.layer_heater)
    trans1.connect(port='e1', destination=heater.ports['W'])
    pad1 = D << metal.rd_pad(size=(pad_size, pad_size), corner_radi=5, layer=ly.layer_heater)
    pad1.connect(port='e3', destination=trans1.ports['e2'])
    outpad1 = D << pg.compass(size=(metal.M_ROUTE_WIDTH, metal.M_ROUTE_WIDTH), layer=ly.layer_metal)
    outpad1.move((-pad_size*2.5, -pad_size))
    D.add_port(name='le1', port=outpad1.ports['W'])
    D.add_port(name='le2', port=outpad1.ports['N'])
    D.add_port(name='le3', port=outpad1.ports['E'])
    D.add_port(name='le4', port=outpad1.ports['S'])
    
    trans2 = D << metal.mt_sine_trans(width1=width, width2=pad_size+10, length=pad_size*2, offset=-pad_size, layer=ly.layer_heater)
    trans2.connect(port='e1', destination=heater.ports['E'])
    pad2 = D << metal.rd_pad(size=(pad_size, pad_size), corner_radi=5, layer=ly.layer_heater)
    pad2.connect(port='e1', destination=trans2.ports['e2'])
    outpad2 = D << pg.compass(size=(metal.M_ROUTE_WIDTH, metal.M_ROUTE_WIDTH), layer=ly.layer_metal)
    outpad2.move((length+pad_size*2.5, -pad_size))
    D.add_port(name='re1', port=outpad2.ports['W'])
    D.add_port(name='re2', port=outpad2.ports['N'])
    D.add_port(name='re3', port=outpad2.ports['E'])
    D.add_port(name='re4', port=outpad2.ports['S'])

    return D
