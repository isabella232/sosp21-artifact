import digi
import digi.on as on
from digi import logger
from digi.util import deep_get, patch_spec, deep_set

import time

_measure = ("bench.digi.dev", "v1", "measures", "measure-test", "default")
_forward_set = False
_backward_set = False

p, b = "", 0


# intent
@on.control
def h1(sv, pv):
    # benchmark
    global _forward_set
    if deep_get(sv, "brightness.intent") == 0.1 and not _forward_set:
        print("bench: setting forward leaf")
        resp, e = patch_spec(*_measure, {
            "obs": {
                "forward_leaf": time.time()
            }
        })
        if e is None:
            _forward_set = True

    global p, b
    p, b = deep_get(sv, "power.intent"), deep_get(sv, "brightness.intent")

    # XXX this is a mock lamp, use digi-phy/lamp
    # for real device actuation
    time.sleep(0.2)

    # update status
    patch = {
        "control": {
            "power": {
                "status": p,
            },
            "brightness": {
                "status": b,
            },
        }
    }

    resp, e = patch_spec(*digi.auri, patch)
    if e is not None:
        logger.error(f"unable to update status {e}")

    # benchmark
    print("bench: setting backward leaf")
    global _backward_set
    if b == 0.1 and not _backward_set:
        resp, e = patch_spec(*_measure, {
            "obs": {
                "backward_leaf": time.time()
            }
        })
        if e is None:
            _backward_set = True


if __name__ == '__main__':
    digi.run()
