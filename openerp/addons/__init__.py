
import os
import sys
import imp

import cherrypy


ADDONS_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ADDONS_PATH)


class Graph(dict):

    def addNode(self, name, deps):
        max_depth, father = 0, None
        for n in [Node(x, self) for x in deps]:
            if n.depth >= max_depth:
                father = n
                max_depth = n.depth
        if father:
            father.addChild(name)
        else:
            Node(name, self)

    def __iter__(self):
        level = 0
        done = set(self.keys())
        while done:
            level_modules = [(name, module) for name, module in self.items() if module.depth==level]
            for name, module in level_modules:
                done.remove(name)
                yield module
            level += 1


class Singleton(object):
    def __new__(cls, name, graph):
        if name in graph:
            inst = graph[name]
        else:
            inst = object.__new__(cls)
            inst.name = name
            graph[name] = inst
        return inst


class Node(Singleton):

    def __init__(self, name, graph):
        self.graph = graph
        if not hasattr(self, 'children'):
            self.children = []
        if not hasattr(self, 'depth'):
            self.depth = 0

    def addChild(self, name):
        node = Node(name, self.graph)
        node.depth = self.depth + 1
        if node not in self.children:
            self.children.append(node)
        for attr in ('init', 'update', 'demo'):
            if hasattr(self, attr):
                setattr(node, attr, True)
        self.children.sort(lambda x, y: cmp(x.name, y.name))

    def __setattr__(self, name, value):
        super(Singleton, self).__setattr__(name, value)
        if name in ('init', 'update', 'demo'):
            tools.config[name][self.name] = 1
            for child in self.children:
                setattr(child, name, value)
        if name == 'depth':
            for child in self.children:
                setattr(child, name, value + 1)

    def __iter__(self):
        return itertools.chain(iter(self.children), *map(iter, self.children))

    def __str__(self):
        return self._pprint()

    def _pprint(self, depth=0):
        s = '%s\n' % self.name
        for c in self.children:
            s += '%s`-> %s' % ('   ' * depth, c._pprint(depth+1))
        return s

def create_graph(module_list, force=None):
    graph = Graph()
    upgrade_graph(graph, module_list, force)
    return graph

def upgrade_graph(graph, module_list, force=None):
    
    if force is None:
        force = []
        
    packages = []
    len_graph = len(graph)
    
    for module in module_list:
        
        mod_path = os.path.join(ADDONS_PATH, module)
        terp_file = os.path.join(ADDONS_PATH, module, '__terp__.py')
        
        if not mod_path or not terp_file:
            continue
        
        if os.path.isfile(terp_file):
            try:
                info = eval(open(terp_file).read())
            except:
                cherrypy.log('module %s: eval file %s' % (module, terp_file), "ERROR")
                raise
            if info.get('installable', True):
                packages.append((module, info.get('depends', []), info))

    dependencies = dict([(p, deps) for p, deps, data in packages])
    current, later = set([p for p, dep, data in packages]), set()
    
    while packages and current > later:
        package, deps, data = packages[0]

        # if all dependencies of 'package' are already in the graph, add 'package' in the graph
        if reduce(lambda x, y: x and y in graph, deps, True):
            if not package in current:
                packages.pop(0)
                continue
            later.clear()
            current.remove(package)
            graph.addNode(package, deps)
            node = Node(package, graph)
            node.data = data
        else:
            later.add(package)
            packages.append((package, deps, data))
        packages.pop(0)

    for package in later:
        unmet_deps = filter(lambda p: p not in graph, dependencies[package])
        cherrypy.log('module %s: Unmet dependencies: %s' % (package, ', '.join(unmet_deps)), "ERROR")

    result = len(graph) - len_graph
    if result != len(module_list):
        cherrypy.log('Not all modules have loaded.', "ERROR")
        
    return result


def imp_module(name):
    fp, pathname, description = imp.find_module(name, [ADDONS_PATH])
    try:
        return imp.load_module(name, fp, pathname, description)
    finally:
        if fp:
            fp.close()
            

def load_addons(config):
    
    addons = [f for f in os.listdir(ADDONS_PATH) \
              if os.path.isfile(os.path.join(ADDONS_PATH, f, "__terp__.py"))]
              
    
    sys.modules.pop("openerp.addons", None)
    
    graph = create_graph(addons)
    
    for package in graph:
                
        cherrypy.log("Loading module '%s'" % package.name, "INFO")
        
        m = imp_module(package.name)
                
        static = os.path.join(ADDONS_PATH, package.name, "static")
        if os.path.isdir(static):
            base = imp_module("base")
            base.widgets.register_resource_directory(config, package.name, static)

