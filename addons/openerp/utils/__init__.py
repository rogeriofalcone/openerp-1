import rpc
import rpc_utils
from openobject.tools import register_template_vars
from tools import *
from utils import *


def _root_vars():
    return {
        'rpc': rpc,
    }

register_template_vars(_root_vars, None)

del register_template_vars
