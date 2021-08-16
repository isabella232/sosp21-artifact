# ipython utils
import os
import sys
import time
import yaml
import datetime
from pathlib import Path

from IPython import get_ipython 
from IPython.core.magic import (register_line_magic, register_cell_magic,
                                register_line_cell_magic)

import warnings; warnings.simplefilter('ignore')

start = time.time()

@register_line_cell_magic
def elapsed_time(line, cell=None):
    if cell is not None:
        get_ipython().run_cell(cell)
    print(datetime.timedelta(seconds=round(time.time() - start)))


os.environ.update({
    "GROUP": "tutorial",
    "VERSION": "v1",
    "KOPFLOG": "false",
    "DOCKER_TLS_VERIFY": "1",
    "DOCKER_HOST": "tcp://127.0.0.1:32770",
    "DOCKER_CERT_PATH": str(Path(os.environ["HOME"], ".minikube/certs")),
    "MINIKUBE_ACTIVE_DOCKERD": "minikube",
    "IMAGEPULL": "Never",
    "REPO": "tutorial",
})


workdir = (Path(os.environ["GOPATH"], 
               "src", "digi.dev", 
               "tutorial", "workdir"))
os.environ["WORKDIR"] = str(workdir)


def _rm_tree(pth):
    pth = Path(pth)
    
    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            _rm_tree(child)
    pth.rmdir()
      
def create(m: str, new=True):
    y = yaml.load(m, Loader=yaml.FullLoader)
    assert "kind" in y
    _dir = Path(workdir, y["kind"].lower())
   
    if _dir.is_dir() and new:
        _rm_tree(_dir)
    Path(_dir, "driver").mkdir(parents=True, exist_ok=True)
    Path(_dir, "deploy").mkdir(parents=True, exist_ok=True)
    Path(_dir, "deploy", "cr_run.yaml").touch()
    Path(_dir, "driver", "handler.py").touch()
    with open(Path(_dir, "model.yaml"), "w") as f:
        f.write(m)
            
def handler_file(k):
    return Path(workdir, k, "driver", "handler.py")

def model_file(k, new=True):
    if new:
        return Path(workdir, k, "deploy", "cr.yaml")
    else:
        return Path(workdir, k, "deploy", "cr_run.yaml")