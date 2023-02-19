# Circuit Parser
## Graph Construction
- Put `.v` and `.lib` to OpenSTA to generate `.sdf` file, which contains cell delay and net delay, we can construct the circuit graph based on these connections


## Documentation for DGL
- [https://docs.dgl.ai/index.html](https://docs.dgl.ai/index.html)

## Data Format from Repo
- [https://github.com/TimingPredict/Dataset](https://github.com/TimingPredict/Dataset)

## Edges (3 types)
### `cell_out`
- fanin $\rightarrow$ fanout
- cell arcs.

Features:

-   `2*4*(1+7+7)x`: [E/L]\* cell\_{rise, fall}, {rise, fall}\_transition {is\_valid, xindex, yindex}
-   `2*4*49x`: [E/L]\* cell\_{rise, fall}, {rise, fall}\_transition values
-   `4x`: cell delay annotations (EL/RF)


- Edge type = cell_out
  - fea_name = e_cell_delays, fea_scheme = Scheme(shape=(4,), dtype=torch.float32)
  - fea_name = ef, fea_scheme = Scheme(shape=(512,), dtype=torch.float32)

### `net_out`
- net arc
- net driver $\rightarrow$ net sink
- `2x`: relative position
- Edge type = net_out
  - fea_name = ef, fea_scheme = Scheme(shape=(2,), dtype=torch.float32)

### `net_in`
- net arc
- net sink $\rightarrow$ net driver
- `2x`: relative position
- Edge type = net_in
  - fea_name = ef, fea_scheme = Scheme(shape=(2,), dtype=torch.float32)


### Node (1 type)
#### `node`
each node is pin
Features:
- `nf`
  - `1x`: is primary I/O pin (1) or not (0)
  - `1x`: is fanin (0) or fanout (1)
  - `4x`: relative to the top/left/right/bottom of die area
  - `4x`: capacitance information (EL/RF) in cell library
- `4x`: net delay annotations (EL/RF) for fanin pins
- `4x`: arrival time annotations (EL/RF)
- `4x`: slew annotations (EL/RF)
- `1x`: is timing endpoint (i.e. has constraint) (1) or not (0)
- `4x`: required arrival time annotations (EL/RF)

Node type = node
- fea_name = n_rats, fea_scheme = Scheme(shape=(4,), dtype=torch.float32)
- fea_name = n_net_delays, fea_scheme = Scheme(shape=(4,), dtype=torch.float32)
- fea_name = n_ats, fea_scheme = Scheme(shape=(4,), dtype=torch.float32)
- fea_name = n_slews, fea_scheme = Scheme(shape=(4,), dtype=torch.float32)
- fea_name = nf, fea_scheme = Scheme(shape=(10,), dtype=torch.float32)
- fea_name = n_is_timing_endpt, fea_scheme = Scheme(shape=(), dtype=torch.float32)
