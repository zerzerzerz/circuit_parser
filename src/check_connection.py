def check_net_connection(net_out, net_delay):
    print("Checking net connection from net_out (verilog) and net_out (.sdf file, net delay)")
    n1 = set(net_out)
    n2 = set(net_delay.keys())

    diff = n1.difference(n2)
    if len(diff) > 0:
        print("net connection in verilog but bot in .sdf")
        print(diff)
    
    diff = n2.difference(n1)
    if len(diff) > 0:
        print("net connection in .sdf but bot in verilog")
        print(diff)


def check_cell_connection(cell_out, cell_delay):
    print("Checking cell connection from cell_out (verilog) and cell_out (.sdf file, cell delay)")
    n1 = set(cell_out)
    n2 = set(cell_delay.keys())

    diff = sorted(list(n1.difference(n2)))
    if len(diff) > 0:
        print("cell connection in verilog but bot in .sdf")
        for d in diff:
            print(d)
    
    diff = sorted(list(n2.difference(n1)))
    if len(diff) > 0:
        print("cell connection in .sdf but bot in verilog")
        for d in diff:
            print(d)