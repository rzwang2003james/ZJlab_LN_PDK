import sys
import os
from phidl import Device, quickplot

# Add lnzj-pdk to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "lnzj-pdk"))

# Import building blocks
from zjlab_ln.passive.wg import dc,wg,tp
from zjlab_ln.active.metal import gsg_seg_wg


if __name__ == "__main__":
    # Make a top-level device
    top = Device("top")

    # Create a directional coupler
    dc_dev = top << dc()

    # Create a GSG taper
    gsg = top << gsg_seg_wg(termination = False)
    gsg.connect(port='o3', destination=dc_dev.ports['o2'])
    
    # Create a directional coupler
    dc_dev2 = top << dc()
    dc_dev2.connect(port='o1', destination=gsg.ports['o4'])

    # Plot
    quickplot(top)
    
    # Export to GDS
    top.write_gds("test.gds")
