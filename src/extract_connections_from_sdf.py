import re
from config import CELL_PIN_SEP

def extract_connections_from_sdf(sdf_file):
    with open(sdf_file, 'r') as f:
        sdf_content = f.read()
    
    inter_connections = extract_inter_connections_from_sdf_content(sdf_content)
    inner_connections = extract_inner_connections_from_sdf_content(sdf_content)
    return inter_connections, inner_connections


def extract_inter_connections_from_sdf_content(sdf_content):
    """
    INTERCONNECT req_msg[31] input25/A (
    """
    inter_connections = []
    p = re.compile(r"INTERCONNECT\s+(.*?)\s+(.*?)[\s\(\)]")
    for item in p.findall(sdf_content):
        src = item[0].replace('/', CELL_PIN_SEP)
        dst = item[1].replace('/', CELL_PIN_SEP)
        inter_connections.append((src, dst))
    return inter_connections


def extract_inner_connections_from_sdf_content(sdf_content):
    """
    (CELL
        (CELLTYPE "NAND2_X4")
        (INSTANCE _415_)
        (DELAY
            (ABSOLUTE
                (IOPATH A1 ZN (0.016::0.016) (0.014::0.015))
                (IOPATH A2 ZN (0.019::0.021) (0.019::0.021))
            )
        )
    )
    """
    # CELLTYPE "NAND2_X4" ) ( INSTANCE _415_ )
    # IOPATH A2 ZN (
    p = re.compile(r"(CELLTYPE)\s*\"?(.*?)\"?\s*\)\s*\(\s*INSTANCE\s*(.*?)\s*\)|(IOPATH)\s+(.*?)\s+(.*?)[\s\(\)]")
    inner_connections = []
    cell_type = cell_name = src = dst = None
    for item in p.findall(sdf_content):
        if item[0] == "CELLTYPE":
            cell_type = item[1]
            cell_name = item[2]
        elif item[3] == "IOPATH":
            src = item[4]
            dst = item[5]
            inner_connections.append((
                cell_type,
                cell_name,
                src,
                dst
            ))
        else:
            raise RuntimeError(f"item = {item}")

    tmp = list(set(inner_connections))
    inner_connections = []
    for item in tmp:
        inner_connections.append({
            "cell_type": item[0],
            "cell_name": item[1],
            "src_pin": item[2],
            "dst_pin": item[3],
        })
    
    return inner_connections