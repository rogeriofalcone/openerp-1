{
    "name" : "OpenERP Web Diagram",
    "category" : "Hidden",
    "version" : "2.0",
    "depends" : ["base"],
    "js": [
        'static/lib/js/raphael-min.js',
        'static/lib/js/dracula_graffle.js',
        'static/lib/js/dracula_graph.js',
        'static/lib/js/dracula_algorithms.js',
        'static/src/js/diagram.js'
    ],
    'css' : [
        "static/src/css/base_diagram.css",
    ],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    'active': True,
}
