from config.config import FANOUTS
import utils.utils as utils

def extract_inter_connection(cells:list) -> dict:
    connections = {}
    for cell in cells:
        cell_name = cell['cell_name']
        for pin in cell['pins']:
            pin_name = cell_name + '.' + pin[0]
            wire_name = pin[1]

            if wire_name in connections.keys():
                pass
            else:
                connections[wire_name] = {
                    "driver": [],
                    "sink": [],
                }
            
            if pin[0] in FANOUTS:
                # fanout connected to this wire/port
                connections[wire_name]['driver'].append(pin_name)
            else:
                # fanin connected to this wire/port
                connections[wire_name]['sink'].append(pin_name)

    return connections