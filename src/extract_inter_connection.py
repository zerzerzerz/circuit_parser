
def extract_inter_connection(cells:list, fanin_or_fanout:dict) -> dict:
    connections = {}
    for cell in cells:
        cell_name = cell['cell_name']
        cell_class = cell['cell_class']
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
            
            if pin[0] in fanin_or_fanout[cell_class]['output']:
                # fanout connected to this wire/port
                connections[wire_name]['driver'].append(pin_name)
            else:
                # fanin connected to this wire/port
                connections[wire_name]['sink'].append(pin_name)

    return connections