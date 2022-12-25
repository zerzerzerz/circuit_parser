def get_pin_fanin_or_fanout(lut_info):
    pin_fanin_or_fanout = {}
    for cell_class, cell in lut_info.items():
        pin_fanin_or_fanout[cell_class] = {"input":[], "output":[]}
        for pin_name, pin in cell.items():
            direction = pin['direction']
            pin_fanin_or_fanout[cell_class][direction].append(pin_name)
    return pin_fanin_or_fanout