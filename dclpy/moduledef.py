

class ModuleNotFound(Exception):
    pass


class ModuleDef(object):
    name =  ''
    paths = []
    modules = []

    def __init__(self, name_mod, path_mods):
        self.name = name_mod
        self.paths = path_mods

        # Importa os modulos e pega seus 
        # caminhos absolutos
        self.modules = [
            __import__(x).__file__ 
            for x in path_mods
        ]

        # remove o pyc se necessario
        self.modules = [
            x[:-1] if x.endswith('pyc') else x
            for x in self.modules
        ]

    def has(self, cls):
        return cls in self.modules

    def __str__(self):
        return "\"%s\"" % (self.name)


