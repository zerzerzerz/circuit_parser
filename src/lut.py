'''
Extract LUT information from .lib file.
If a function starts with `get`, it means only get the string without parsing it.
Real parsing function starts with `parse`.
'''
import re
from einops import rearrange, repeat
import collections
from config import CELL_PIN_SEP, LUT
import copy
from config import CONNECTION_SEP,VERBOSE
import numpy as np
import torch




def get_cell_content(liberty_file):
    '''
    return a dict
    cell_class -> cell_content
    each cell corresponds to a string which contains pin information
    cell_content = pin(){}, pin(){}, pin(){}, ..., pin(){}
    '''
    print("\tExtracting cell content")
    with open(liberty_file) as f:
        c = f.read()
    # cell ( "sky130_fd_sc_hd__sdfxbp_1" ) {
    p = re.compile(r'cell\s*\(\s*\"?(\w+)\"?\s*\)\s*\{')
    cell_header = True
    cells = {}
    while cell_header is not None:
        cell_header = p.search(c)
        if cell_header is None:
            break
        else:
            cell_class = cell_header.group(1)
            s = cell_header.span()[-1]
            stack_num = 1
            while stack_num != 0:
                if c[s] == '{':
                    stack_num += 1
                elif c[s] == '}':
                    stack_num -= 1
                else:
                    pass
                s += 1
            cell_content = c[cell_header.span()[0]:s]
            cells[cell_class] = cell_content
            c = c[s:]
    
    # utils.save_json(cells, 'tmp.json')
    return cells
            

def get_pin_content(cell_contents):
    '''
    return a dict
    cell_class -> pin_name -> pin_content
    each pin corresponds to a string
    '''
    print("\tExtract pin content")
    res = {}
    # pin ( "SCD" ) {
    p = re.compile(r'pin\s*\(\s*\"?(\w+)\"?\s*\)\s*{')
    for cell_class, cell_content in cell_contents.items():
        res[cell_class] = {}
        pin_header = True
        while pin_header is not None:
            pin_header = p.search(cell_content)
            if pin_header is None:
                break
            else:
                pin_name = pin_header.group(1)
                i = pin_header.span()[-1]
                stack_flag = 1
                while stack_flag != 0:
                    if cell_content[i] == '{':
                        stack_flag += 1
                    elif cell_content[i] == '}':
                        stack_flag -= 1
                    else:
                        pass
                    i += 1
                res[cell_class][pin_name] = cell_content[pin_header.span()[0]:i]
                cell_content = cell_content[i:]
    return res


def parse_pin_content(cell_pin_dict):
    print("\tParsing pin content")
    ans = collections.defaultdict(lambda : {})

    # direction : "input" ;
    p_direction = re.compile(r'direction\s*\:\s*\"?(\w+)\"?\s*;')

    # capacitance : 0.0017320000 ;
    # fall_capacitance	: 1.093689 ;
    # rise_capacitance	: 1.162619 ;
    # max_capacitance		: 484.619000 ;
    # only match capacitance for input pin!!!
    p_cap = re.compile(r'\bcapacitance\s*\:\s*([+-]?\d*\.?\d+)\s*;')
    for cell_class in cell_pin_dict.keys():
        for pin_name, pin_content in cell_pin_dict[cell_class].items():
            # find direction
            direction = p_direction.search(pin_content)
            if direction is None:
                continue
            else:
                direction = direction.group(1)
            if direction not in ['input','output']:
                if VERBOSE:
                    print(f'direction of {cell_class}{CELL_PIN_SEP}{pin_name} is {direction}, not implemented, continue')
                continue
            else:
                pass

            # find capacitance
            if direction == "input":
                cap = p_cap.search(pin_content)
                if cap is None:
                    if VERBOSE:
                        print(f'cap for {cell_class}{CELL_PIN_SEP}{pin_name} is not found, use 0.0 to replace')
                    cap = 0.0
                else:
                    cap = float(cap.group(1))
            else:
                cap = 0.0
            
            ans[cell_class][pin_name] = {
                "direction": direction,
                "capacitance": cap,
            }

            # find LUTs
            if 'timing' in pin_content and direction == 'output':
                timing_contents = get_timing_content(pin_content)
                ans[cell_class][pin_name]['luts'] = {}
                for related_pin in timing_contents.keys():
                    ans[cell_class][pin_name]['luts'][related_pin] = parse_lut(timing_contents[related_pin])
    

    return ans


def get_timing_content(pin_content):
    '''
    There are many `timing ( ) { }` in a pin content
    A timing content corresponds to a related_pin
    return a dict:
        related_pin -> timing content
    '''
    ans = {}
    # timing ( ) {
    p_timing = re.compile(r'timing\s*\(\s*\)\s*\{')
    # related_pin : "B1" ;
    p_related_pin = re.compile(r'related_pin\s*\:\s*\"?(\w+)\"?\s*;')

    timing_header = True
    while timing_header is not None:
        # extrac a timing content
        timing_header = p_timing.search(pin_content)
        if timing_header is None:
            break
        else:
            i = timing_header.span()[-1]
            stack_flag = 1
            while stack_flag != 0:
                if pin_content[i] == '{':
                    stack_flag += 1
                elif pin_content[i] == '}':
                    stack_flag -= 1
                else:
                    pass
                i += 1
            timing_content = pin_content[timing_header.span()[0]:i]
            pin_content = pin_content[i:]

            # extract related_pin
            related_pin = p_related_pin.search(timing_content)
            if related_pin is None:
                continue
            else:
                related_pin = related_pin.group(1)
            ans[related_pin] = timing_content
    return ans


def parse_lut(timing_content):
    '''
    parse luts from a timing content
    there are many luts in a timing content
    return a list
    '''
    tmp = []
    res = []
    # rise_transition ( "del_1_7_7" ) {
    p = re.compile(r'\w+\s*\(\s*\"?\w+\"?\s*\)\s*{')

    table_header = True
    while table_header is not None:
        table_header = p.search(timing_content)
        if table_header is None:
            break
        else:
            i = table_header.span()[-1]
            stack_flag = 1
            while stack_flag != 0:
                if timing_content[i] == '{':
                    stack_flag += 1
                elif timing_content[i] == '}':
                    stack_flag -= 1
                else:
                    pass
                i += 1
            
            # extract a table
            table = timing_content[table_header.span()[0]:i]
            timing_content = timing_content[i:]
            tmp.append(table)

    for table in tmp:
        # only reserve {...}
        # remove space char
        table = re.search(r'\{([\s\S]*?)\}', table).group(1)
        for char in ['\n', '\t', ' ', '\"', '\\']:
            table = table.replace(char,'')
        
        table_split = table.split(';')

        # these len are original length of index and table
        len_index1 = len_index2 = len_values = 0
        if len(table_split) == 4:
            index1, index2, values, _ = table_split
            index1 = parse_index_or_value(index1)
            index2 = parse_index_or_value(index2)
            values = parse_index_or_value(values)
            len_index1 = len(index1)
            len_index2 = len(index2)
            len_values = len(values)
            
        elif len(table_split) == 3:
            index1, values, _ = table_split
            index1 = parse_index_or_value(index1)
            index2 = copy.copy(index1)
            values = parse_index_or_value(values)
            len_index1 = len(index1)
            len_index2 = 0
            len_values = len(values)

        elif len(table_split) == 2:
            index1 = [0.0 for i in range(LUT.lut_size)]
            index2 = [0.0 for i in range(LUT.lut_size)]
            values, _ = table_split
            values = parse_index_or_value(values)
            len_index1 = 0
            len_index2 = 0
            len_values = len(values)
        else:
            raise NotImplementedError
        
        res.append(regularize_lut({
            "index1": index1,
            "index2": index2,
            "values": values,
            "len_index1": len_index1,
            "len_index2": len_index2,
            "len_values": len_values,
        }))

    return res


def parse_index_or_value(line):
    '''
    index_1(0.0100000000,0.0230506000,0.0531329000,0.1224740000,0.2823110000,0.6507430000,1.5000000000)
    return a list
    each item is a float
    '''
    line = re.search(r'\w+\(([\s\S]*?)\)', line).group(1)
    line = line.split(',')
    line = [float(i) for i in line]
    return line


def regularize_lut(lut):
    '''
    lut is a dict
    index1, index2, values are its keys
    len_index1, len_index2, len_values are also its keys to represent the original length of index and value
    regularize index and value to have a size of LUT.size and LUT.size ** 2
    '''
    # for index1
    index1 = lut['index1']
    if len(index1) < LUT.lut_size:
        index1 = index1 + [0.0] * (LUT.lut_size - len(index1))
    else:
        index1 = index1[0:LUT.lut_size]
    
    # for index2
    index2 = lut['index2']
    if len(index2) < LUT.lut_size:
        index2 = index2 + [0.0] * (LUT.lut_size - len(index2))
    else:
        index2 = index2[0:LUT.lut_size]
    
    # for values
    # get original length of index and value
    len_index1 = lut['len_index1']
    len_index2 = lut['len_index2']

    # this is a 1d tensor
    values = torch.Tensor(lut['values'])

    if len_index1 == 0 and len_index2 == 0:
        if values.nelement() > 0:
            values = [values.flatten()[0].item()] * LUT.lut_size**2
        else:
            values = [0.0] * LUT.lut_size**2

    elif len_index1 != 0 and len_index2 == 0:
        if len_index1 < LUT.lut_size:
            values = torch.cat([values, torch.zeros(LUT.lut_size - len_index1)], dim=0)
        else:
            values = values[0:LUT.lut_size]
        values = repeat(values, 'a -> a b', b=LUT.lut_size).flatten().tolist()

    elif len_index1 != 0 and len_index2 != 0:
        values = values.reshape(len_index1, len_index2)
        if len_index1 < LUT.lut_size:
            values = torch.cat([
                values,
                torch.zeros(LUT.lut_size-len_index1, values.shape[1])
            ], dim=0)
        else:
            values = values[0:LUT.lut_size,:]

        if len_index2 < LUT.lut_size:
            values = torch.cat([
                values,
                torch.zeros(values.shape[0], LUT.lut_size - len_index2)
            ], dim=1)
        else:
            values = values[:,0:LUT.lut_size]

        values = values[0:LUT.lut_size, 0:LUT.lut_size].flatten().tolist()

    else:
        raise NotImplementedError(f'len_index1 = {len_index1}, len_index2 = {len_index2}')

    # if len(values) < LUT.lut_size**2:
    #     values = values + [0.0] * (LUT.lut_size**2 - len(values))
    # else:
    #     values = values[0:LUT.lut_size**2]

    if not isinstance(values, list):
        values = values.flatten().tolist()
    
    return {
        "index1": index1,
        "index2": index2,
        "values": values,
    }


def extract_lut_single_file(liberty_file):
    """
    Extract information from a single liberty file
    """
    cell_content = get_cell_content(liberty_file)
    pin_content = get_pin_content(cell_content)
    res = parse_pin_content(pin_content)
    return res


def extract_lut(liberty_files):
    """
    Extract information in many .lib (liberty) files
    """
    print("Extracting LUTs from .lib")
    assert isinstance(liberty_files, list)
    tmp = []
    for f in liberty_files:
        print(f"\tExtracting LUT in {f}")
        tmp.append(extract_lut_single_file(f))
    
    print('\tMerging all .lib files together')
    ans = {}
    for item in tmp:
        for k,v in item.items():
            if k in ans.keys():
                continue
            else:
                ans[k] = v
    ans = {
        k: ans[k] for k in sorted(ans.keys())
    }
    return ans

