import digi
import digi.on as on
from digi import logger
from digi.util import deep_get, patch_spec, deep_set

import time
import threading

_poll = None
_dev = None

_measure = ("bench.digi.dev", "v1", "measures", "measure-test", "default")
_forward_set = False
_backward_set = False


class _Poll(threading.Thread):
    def __init__(self, dev, interval=0.01):
        threading.Thread.__init__(self)
        self.dev = dev
        self.interval = interval
        self.stop_flag = False

    def run(self):
        while True:
            if self.stop_flag:
                break

            global p, b
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
            global _backward_set
            if b == 0.1 and not _backward_set:
                resp, e = patch_spec(*_measure, {
                    "obs": {
                        "backward_leaf": time.time()
                    }
                })
                if e is None:
                    _backward_set = True

            time.sleep(self.interval)


# meta
@on.meta
def h0(sv):
    e = sv.get("endpoint", None)
    if e is None:
        return

    if _poll is not None:
        _poll.stop_flag = True

    _p = _Poll(dev=_dev,
               interval=sv.get("poll_interval", 0.01))
    _p.start()


# intent
@on.control
def h1(sv, pv):
    global _dev
    if _dev is None:
        return

    # benchmark
    global _forward_set
    if deep_get(sv, "brightness.intent") == 0.1 and not _forward_set:
        resp, e = patch_spec(*_measure, {
            "obs": {
                "forward_leaf": time.time()
            }
        })
        if e is None:
            _forward_set = True

    global p, b
    p, b = deep_get(sv, "power.intent"), deep_get(sv, "brightness.intent")
    deep_set(sv, "power.status", p)
    deep_set(sv, "brightness.status", b)


if __name__ == '__main__':
    digi.run()
