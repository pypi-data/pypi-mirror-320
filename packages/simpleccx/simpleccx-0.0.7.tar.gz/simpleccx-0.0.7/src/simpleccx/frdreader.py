from collections import namedtuple
import pandas as pd


NODAL_FIELDS = (
    "NODES",
    "CP3DF",
    "CT3D-MIS",
    "CURR",
    "DEPTH",
    "DISP",
    "DTIMF",
    "ELPOT",
    "EMFB",
    "EMFE",
    "ENER",
    "ERROR",
    "FLUX",
    "FORC",
    "HCRIT",
    "M3DF",
    "MAFLOW",
    "MDISP",
    "MESTRAIN",
    "MSTRAIN",
    "MSTRESS",
    "NDTEMP",
    "PDISP",
    "PE",
    "PFORC",
    "PNDTEMP",
    "PS3DF",
    "PSTRESS",
    "PT3DF",
    "RFL",
    "SDV",
    "SEN",
    "STPRES",
    "STRESS",
    "STRMID",
    "STRNEG",
    "STRPOS",
    "STTEMP",
    "THSTRAIN",
    "TOPRES",
    "TOSTRAIN",
    "TOTEMP",
    "TS3DF",
    "TT3DF",
    "TURB3DF",
    "V3DF",
    "VELO",
    "VSTRES",
    "ZZSTR",
)


Node = namedtuple("Node", "index x y z")
Element = namedtuple("Element", "index type nodes")

def get_nodes(lines, linenr):
    n = int(lines[linenr].split()[1])
    linenr += 1
    print(f"Reading data for {n} nodes")

    def parse_node(line):
        spl = line.split()
        try:
            return Node(int(spl[1]), float(spl[2]), float(spl[3]), float(spl[4]))
        except ValueError:
            return Node(int(line[4:12]), float(line[12:24]), float(line[24:36]), float(line[36:48]))

    nodes = {}
    for _ in range(n):
        node = parse_node(lines[linenr])
        linenr += 1
        nodes[node.index] = node

    return nodes, n


def get_elements(lines, linenr):
    n = int(lines[linenr].split()[1])
    linenr += 1

    print(f"Reading data for {n} elements")

    def parse_element(line):
        line = line.split()
        return Element(int(line[1]), int(line[2]), [int(node) for node in line[5:] if node != "-2"])

    elements = {}
    element_number = 0
    while element_number < n:
        _, element_number, element_type, _, _ = lines[linenr].split()
        element_number = int(element_number)
        element_type = int(element_type)
        if element_type == 4:  # he20
            line = " ".join(lines[linenr:linenr + 3])
            elements[element_number] = parse_element(line)
            linenr += 3
        else:
            raise ValueError(f"Unknown element type {element_type}")

    return elements, 3 * n


def get_results(lines, linenr):
    orig_linenr = linenr
    time = float(lines[linenr].split()[2])
    n = int(lines[linenr].split()[3])
    linenr += 1

    _, field, ncols, _ = lines[linenr].split()
    ncols = int(ncols)

    linenr += 1

    components = []
    for colnr in range(ncols):
        comp = lines[linenr].split()[1]
        if comp != "ALL":
            components.append(comp)
        else:
            ncols -= 1
        linenr += 1

    indices = [(c * 12, (c + 1) * 12) for c in range(1, ncols + 1)]
    print(f"Reading {field} data for {n} nodes, nr of cols {ncols}: {' '.join(components)}")

    data = {field: {comp: {} for comp in components}}
    for i in range(n):
        line = lines[linenr]
        node = int(line[2:12])
        values = [float(line[a:b]) for a, b in indices]
        # print(node, {col: value for col, value in zip(colnames, values)})
        for component, val in zip(components, values):
            data[field][component][node] = val
        linenr += 1

    # ["DISP"]["D1"][1] -> [field][col][node]
    return time, data, linenr - orig_linenr


class FRDReader:
    def __init__(self, filename=None):
        self.nodes = None
        self.elements = None
        self._results = None
        if filename is not None:
            self.read(filename)

    def read(self, filename):
        self.nodes = []
        self.elements = []
        self._results = {}

        with open(filename, 'r') as f:
            lines = [l.strip() for l in f]

        linenr = 0
        while linenr < len(lines):
            line = lines[linenr]
            skip = 1
            if line.startswith('2C'):  # node data
                self.nodes, skip = get_nodes(lines, linenr)
            elif line.startswith('3C'):  # element data
                self.elements, skip = get_elements(lines, linenr)
            elif line.startswith('100C'):  # results block
                time, data, skip = get_results(lines, linenr)
                if time not in self._results:
                    self._results[time] = {}
                self._results[time].update(data)
            linenr += skip

        self.fields = self._get_fields()

        return self

    @property
    def times(self):
        return list(self._results.keys())

    def results(self, t, field=None, component=None, node=None, delta=0.01):
        # find closest time step, with 'delta' accuracy
        if t not in self._results:
            for t_ in self._results.keys():
                if abs(t_ - t) <= delta:
                    t = t_
                    break
            else:
                raise IndexError(f'No results for time {t} with +- {delta}')

        if field is None:
            return self._results[t]
        if component is None:
            return self._results[t][field]
        if node is None:
            return self._results[t][field][component]
        return self._results[t][field][component][node]

    def _get_fields(self):
        fields = {}
        for nodal_results in self._results.values():
            for f in nodal_results:
                if f not in fields:
                    fields[f] = list(nodal_results[f].keys())
        return fields

    def as_dataframe(self, t):
        data_list = []
        for index, node in self.nodes.items():
            data = {"index": index, "x": node.x, "y": node.y, "z": node.z}

            for field, components in self.fields.items():
                for component in components:
                    data[f"{field}_{component}"] = self.results(t, field, component, index)

            data_list.append(data)

        df = pd.DataFrame(data_list)
        df.set_index("index", inplace=True)
        return df



if __name__ == "__main__":
    frd = FRDReader()
    frd.read(r'wd/model.frd')

    nodes = frd.nodes
    elements = frd.elements

    print('First/last node', list(nodes.values())[0], list(nodes.values())[-1])
    print('First/last element', list(elements.values())[0], list(elements.values())[-1])
    print(len(nodes), len(elements))

    print("Stress", frd.results(1.0, "STRESS", "SXX", 1))

    print(frd.times)
    print(frd.fields)

