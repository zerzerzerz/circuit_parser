from config.config import CELL_PIN_SEP

def merge_pin_loc(pipo_loc, cell_locs, pin2index):
    '''merge all locations of PI, PO and pins'''
    res = {}
    for pipo, loc_xy in pipo_loc.items():
        res[pipo] = loc_xy
    
    for pin_name in pin2index.keys():
        # this is a pin of cell
        if CELL_PIN_SEP in pin_name:
            cell_name, _ = pin_name.split(CELL_PIN_SEP)
            cell_loc_xy = cell_locs[cell_name]["location"]
            res[pin_name] = cell_loc_xy
    return res