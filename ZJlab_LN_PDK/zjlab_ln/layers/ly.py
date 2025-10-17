from phidl import LayerSet
from phidl import Device, geometry as pg

ls = LayerSet()
ls.add_layer(name = 'label', gds_layer = 1, gds_datatype = 0,
             description = 'General label', color = 'Pink')
ls.add_layer(name = 'globalmarker', gds_layer = 2, gds_datatype = 0,
             description = 'Global marker', color = 'LightPink')
ls.add_layer(name = 'patternmarker', gds_layer = 3, gds_datatype = 0,
             description = 'EBL marker', color = 'HotPink')
ls.add_layer(name = 'Aligncheck', gds_layer = 4, gds_datatype = 0,
             description = 'alignment', color = 'DeepPink')
ls.add_layer(name = 'dieetch', gds_layer = 5, gds_datatype = 0,
             description = 'deep etch', color = 'PaleVioletRed')
ls.add_layer(name = 'title', gds_layer = 6, gds_datatype = 0,
             description = 'General label', color = 'MediumVioletRed')
ls.add_layer(name = 'wg', gds_layer = 10, gds_datatype = 0,
             description = 'LN wg', color = 'CadetBlue')
ls.add_layer(name = 'wg_doubleetch', gds_layer = 11, gds_datatype = 0,
             description = 'LN wg deepetched', color = 'SteelBlue')
ls.add_layer(name = 'grating', gds_layer = 12, gds_datatype = 0,
             description = 'bragg_grating', color = 'LightSteelBlue')
ls.add_layer(name = 'ring', gds_layer = 13, gds_datatype = 0,
             description = 'LN ring', color = 'LightBlue')
ls.add_layer(name = 'via', gds_layer = 14, gds_datatype = 0,
             description = 'hole', color = 'PowderBlue')
ls.add_layer(name = 'mc', gds_layer = 15, gds_datatype = 0,
             description = 'mode converter', color = 'LightSkyBlue')
ls.add_layer(name = 'mc2', gds_layer = 16, gds_datatype = 0,
             description = 'mode converter', color = 'SkyBlue')
ls.add_layer(name = 'shield', gds_layer = 17, gds_datatype = 0,
             description = 'mode converter', color = 'CornflowerBlue')
ls.add_layer(name = 'gold1', gds_layer = 20, gds_datatype = 0,
             description = 'Gold electrode', color = 'gold')
ls.add_layer(name = 'gold2', gds_layer = 21, gds_datatype = 0,
             description = '2nd Gold electrode', color = 'goldenrod')
ls.add_layer(name = 'nicr', gds_layer = 22, gds_datatype = 0,
             description = 'heater', color = (0.4,0.5,0.7))
ls.add_layer(name = 'Polemarker', gds_layer = 31, gds_datatype = 0,
             description = 'Poling marker', color = 'Cornsilk')
ls.add_layer(name = 'Poleelectrode', gds_layer = 32, gds_datatype = 0,
             description = 'Poling electrode', color = 'BlanchedAlmond')
ls.add_layer(name = 'Polewindow', gds_layer = 33, gds_datatype = 0,
             description = 'Windows for Poling electrode', color = 'Bisque')
ls.add_layer(name = 'Poleetchwindow', gds_layer = 34, gds_datatype = 0,
             description = 'Etching windows for Poling electrode', color = 'NavajoWhite')
#pu.write_lyp('my_layer_properties_file.lyp', layerset = ls)
layer_label =  ls['label']
layer_PM = ls['patternmarker']
layer_GM = ls['globalmarker']
layer_Aligncheck = ls['Aligncheck']
layer_Detch = ls['dieetch']
layer_title = ls['title']
layer_wg = ls['wg']
layer_wg_deep = ls['wg_doubleetch']
layer_grating = ls['grating']
layer_ring = ls['ring']
layer_via = ls['via']
layer_MC = ls['mc']
layer_MC2 = ls['mc2']
layer_shield = ls['shield']
layer_metal = ls['gold1']
layer_metal2 = ls['gold2']
layer_heater = ls['nicr']
layer_Polemarker = ls['Polemarker']
layer_Pmetal = ls['Poleelectrode']
layer_Pvia = ls['Polewindow']
layer_Pvia2 = ls['Poleetchwindow']

def die_area(width=5000, height=5000, wall=10):
    """
    Build a hollow rectangular frame as a PHIDL Device.

    Args:
        width (float): Outer width of the die.
        height (float): Outer height of the die.
        wall (float): Frame wall thickness.

    Returns:
        Device: A device containing the rectangular frame.
    """
    if width <= 2 * wall or height <= 2 * wall:
        raise ValueError("`wall` must be smaller than width/2 and height/2.")

    D = Device(name=f"die_{width}x{height}_t{wall}")

    # Outer rectangle at origin
    outer = pg.rectangle(size=(width, height), layer=layer_Detch)

    # Inner rectangle moved inward by wall thickness
    inner = pg.rectangle(size=(width - 2 * wall, height - 2 * wall), layer=layer_Detch)
    inner.move(destination=(wall, wall))

    # Create hollow frame
    frame = pg.boolean(A=outer, B=inner, operation='A-B', layer=layer_Detch)

    D << frame

    # Make dicing cross
    cross = D << pg.cross(length=600, width=3, layer=layer_PM)
    cross.move((0, 0))
    cross = D << pg.cross(length=600, width=3, layer=layer_PM)
    cross.move((width, 0))
    cross = D << pg.cross(length=600, width=3, layer=layer_PM)
    cross.move((0, height))
    cross = D << pg.cross(length=600, width=3, layer=layer_PM)
    cross.move((width, height))

    offset = 2000
    cross = D << pg.cross(length=600, width=3, layer=layer_PM)
    cross.move((-offset, -offset))
    cross = D << pg.cross(length=600, width=3, layer=layer_PM)
    cross.move((offset+width, -offset))
    cross = D << pg.cross(length=600, width=3, layer=layer_PM)
    cross.move((-offset, offset+height))
    cross = D << pg.cross(length=600, width=3, layer=layer_PM)
    cross.move((offset+width, offset+height))

    return D
