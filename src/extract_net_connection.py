from config.config import CELL_PIN_SEP, CONNECTION_SEP
from collections import defaultdict

def extract_net_connection(cells, fanin_or_fanout):
    print("Extracting net connection")

    wire2pin = defaultdict(lambda :{"driver":[], "sink":[]})
    for cell_name in cells.keys():
        cell_class = cells[cell_name]["cell_class"]
        pins = cells[cell_name]["pins"]
        for pin in pins:
            pin_name = pin["pin_name"]
            connected_wire = pin["connected_wire"]

            try:
                direction = fanin_or_fanout[cell_class][pin_name]
            except KeyError:
                print(f'direction for {cell_name}{CELL_PIN_SEP}{pin_name} is not found, cell_class={cell_class}')
                continue

            if direction == "input":
                wire2pin[connected_wire]["sink"].append(f"{cell_name}{CELL_PIN_SEP}{pin_name}")
            elif direction == "output":
                wire2pin[connected_wire]["driver"].append(f"{cell_name}{CELL_PIN_SEP}{pin_name}")
            else:
                print(f'direction for {cell_name}{CELL_PIN_SEP}{pin_name} is {direction}, not implemented, cell_class={cell_class}')

    return wire2pin

