import os
import time
import jinja2
import importlib.resources

from . import frdreader
import PIL.Image

CGX = r"C:\Apps\Calculix\cgx.exe"
CCX = r"C:\Apps\Calculix\ccx_dynamic.exe"

mesh_size = 50


class Point:
    __index__ = 0
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.index = Point.__index__
        Point.__index__ += 1

    @property
    def cgx(self):
        return f"pnt { self.name } { self.x } { self.y } { self.z }"

    @property
    def name(self):
        return f"p{self.index}"


class Vector:
    def __init__(self, dx, dy, dz):
        self.dx = dx
        self.dy = dy
        self.dz = dz

    @property
    def magnitude(self):
        return (self.dx ** 2 + self.dy ** 2 + self.dz ** 2) ** 0.5


class Line:
    __index__ = 0
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.index = Line.__index__
        Line.__index__ += 1

    @property
    def cgx(self):
        return f"line { self.name } { self.p1.name } { self.p2.name } { self.divs }"

    @property
    def name(self):
        return f"l{self.index}"

    @property
    def points(self):
        return self.p1, self.p2

    @property
    def length(self):
        return ((self.p1.x - self.p2.x) ** 2 + (self.p1.y - self.p2.y) ** 2) ** 0.5

    @property
    def divs(self):
        return max(2, 2 * int(self.length / mesh_size))


class Surface:
    __index__ = 0
    def __init__(self, l1, l2, l3, l4):
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3
        self.l4 = l4
        self.index = Surface.__index__
        Surface.__index__ += 1

    @property
    def cgx(self):
        return f"surf { self.name } { self.l1.name } { self.l2.name } { self.l3.name } { self.l4.name }"

    @property
    def name(self):
        return f"s{self.index}"

    @property
    def lines(self):
        return self.l1, self.l2, self.l3, self.l4

    @property
    def points(self):
        return self.l1.p1, self.l2.p1, self.l3.p1, self.l4.p1

    @staticmethod
    def from_points(p1, p2, p3, p4):
        l1 = Line(p1, p2)
        l2 = Line(p2, p3)
        l3 = Line(p3, p4)
        l4 = Line(p4, p1)
        return Surface(l1, l2, l3, l4)


class Sweep:
    __index__ = 0
    def __init__(self, surface, direction, material):
        self.surface = surface
        self.direction = direction
        self.material = material
        self.index = Sweep.__index__
        Sweep.__index__ += 1

    @property
    def cgx(self):
        return f"swep { self.surface.name } { self.name } tra { self.direction.dx } { self.direction.dy } { self.direction.dz } { self.divs }"

    @property
    def ccx(self):
        return f"*SOLID SECTION, ELSET=E{ self.name }, MATERIAL={ self.material.name }"

    @property
    def name(self):
        return f"b{self.index}"

    @property
    def length(self):
        return self.direction.magnitude

    @property
    def divs(self):
        return max(2, 2 * int(self.length / (2*mesh_size)))


class IsoMaterial:
    def __init__(self, name, E, nu, T=293):
        self.name = name
        self.E = E
        self.nu = nu
        self.T = T

    @property
    def ccx(self):
        return f"*MATERIAL, NAME={ self.name }\n*ELASTIC, TYPE=ISO\n{ self.E },{ self.nu },{ self.T }"


class OrthoMaterial:
    def __init__(self, name, E1, E2, E3, nu12, nu13, nu23, G12, G13, G23, T=293):
        self.name = name
        self.E1, self.E2, self.E3 = E1, E2, E3
        self.nu12, self.nu13, self.nu23 = nu12, nu13, nu23
        self.G12, self.G13, self.G23 = G12, G13, G23
        self.T = T

    @property
    def ccx(self):
        return f"*MATERIAL, NAME={ self.name }\n*ELASTIC, TYPE=ENGINEERING CONSTANTS\n{ self.E1 },{ self.E2 },{ self.E3 },{ self.nu12 },{ self.nu13 },{ self.nu23 },{ self.G12 },{ self.G13 }\n{ self.G23 },{ self.T }"


class CalculiX:
    DATASETS = [('DISP_D1', 1, 1), ('DISP_D2', 1, 2), ('DISP_D3', 1, 3), ('MESTRAIN_MEXX', 2, 1), ('MESTRAIN_MEYY', 2, 2), ('MESTRAIN_MZZ', 2, 3)]

    def __init__(self, data, model_name="model", working_dir="wd", solver="PARDISO"):
        self.data = data
        self.data["solver"] = solver
        self.data["datasets"] = CalculiX.DATASETS
        self.model_name = model_name
        self.template_text = {}
        self.start_dir = os.getcwd()
        self.working_dir = os.path.join(os.getcwd(), working_dir)

    def get_template(self, fname, name):
        template_str = importlib.resources.read_text("simpleccx.templates", fname)
        self.template_text[name] = template_str
        return jinja2.Environment().from_string(template_str)

    def pre(self):
        os.chdir(self.start_dir)
        fbd = self.get_template("model.fbd.j2", "pre").render(**self.data)

        os.chdir(self.working_dir)
        with open("model.fbd", "w") as f:
            f.write(fbd)

        os.system(f"{ CGX } -bg { self.model_name }.fbd")
        os.system("type DCF* ICF* > ties.sur")
        os.system("del ICF* DCF*")
        os.system("type b*.nam > sweeps.nam")
        os.system("del b*.nam")

        os.chdir(self.start_dir)

    def solve(self):
        os.chdir(self.start_dir)
        inp = self.get_template("model.inp.j2", "solve").render(**self.data)

        os.chdir(self.working_dir)
        with open("model.inp", "w") as f:
            f.write(inp)
        os.system(f"{ CCX } -i { self.model_name }")

        os.chdir(self.start_dir)

    def _post_results(self):
        os.chdir(self.working_dir)
        self.results = frdreader.FRDReader("model.frd")
        os.chdir(self.start_dir)

    def _post_images(self):
        os.chdir(self.start_dir)
        self.data["times"] = self.results.times
        fbd = self.get_template("post.fbd.j2", "post").render(**self.data)

        os.chdir(self.working_dir)
        with open("post.fbd", "w") as f:
            f.write(fbd)

        os.system(f"{ CGX } -b post.fbd")

        self.results = frdreader.FRDReader("model.frd")
        self.results.images = {}
        for step, time in enumerate(self.results.times):
            self.results.images[time] = {ds_name: PIL.Image.open(f"hcpy_{i+1 + step*len(CalculiX.DATASETS)}.png") for i, (ds_name, _, _) in enumerate(CalculiX.DATASETS)}

        os.chdir(self.start_dir)

    def post(self):
        self._post_results()
        self._post_images()

    def go(self):
        start_time = time.time()
        self.pre()
        self.solve()
        self.run_time = time.time() - start_time
        self.post()

        return self.results
