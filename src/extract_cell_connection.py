from config.config import CELL_PIN_SEP, CONNECTION_SEP

def extract_cell_connection(cells, lut_info):
    print("Extracting cell_out")
    res = []
    for cell_name in cells.keys():
        cell_class = cells[cell_name]["cell_class"]
        fanin = []
        fanout = []
        for pin in cells[cell_name]["pins"]:
            pin_name = pin["pin_name"]

            try:
                direction = lut_info[cell_class][pin_name]["direction"]
            except KeyError:
                print(f'direction for {cell_name}{CELL_PIN_SEP}{pin_name} is not found in LUT info, cell_class is {cell_class}')
            
            if direction == 'input':
                fanin.append(f'{cell_name}{CELL_PIN_SEP}{pin_name}')
            elif direction == 'output':
                fanout.append(f'{cell_name}{CELL_PIN_SEP}{pin_name}')
            else:
                print(f'direction for {cell_name}{CELL_PIN_SEP}{pin_name} is {direction}, not implemented, cell_class is {cell_class}')

        for f_in in fanin:
            for f_out in fanout:
                res.append(f'{f_in}{CONNECTION_SEP}{f_out}')
    
    return res
