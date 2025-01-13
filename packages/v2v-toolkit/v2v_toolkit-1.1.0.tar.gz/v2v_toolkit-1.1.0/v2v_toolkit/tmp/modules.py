import random
import time
from typing import List

from v2v_toolkit.utils.logs import setup_logger
from v2v_toolkit import Graph, Context
from v2v_toolkit import Module


class A(Module):
    def __init__(
        self,
        name="A",
        depends_on=None,
        workspace=None,
        logger=None,
        **params,
    ):
        self.n = params.pop("n", 10)
        super().__init__(name, depends_on, workspace, logger, **params)

    def run(self, *args, **kwargs):
        data = [i for i in range(self.n)]
        return {"data": data}


class B(Module):
    def __init__(
        self,
        name="B",
        depends_on=None,
        workspace=None,
        logger=None,
        **params,
    ):
        self.p = params.pop("strategy", "sum")
        super().__init__(name, depends_on, workspace, logger, **params)
        self.name = self.name + "_" + self.p

    def run(self, data=None, *args, **kwargs):
        if data is None:
            data = []
        time.sleep(random.randint(1, 5))
        ret = None
        if self.p == "sum":
            ret = 2
        if self.p == "max":
            ret = 1
        if self.p == "min":
            ret = -1
        if self.p == "mean":
            ret = 0
        return {self.produces: ret}


class C(Module):
    def __init__(
        self,
        name="C",
        depends_on=None,
        workspace=None,
        logger=None,
        **params,
    ):
        super().__init__(name, depends_on, workspace, logger, **params)

    def run(self, b1, b2, b3, *args, **kwargs):
        time.sleep(2)
        return {"c1": 1, "c2": 2, "c3": 3}


class D(Module):
    def __init__(
        self,
        name="D",
        depends_on=None,
        workspace=None,
        logger=None,
        **params,
    ):
        super().__init__(name, depends_on, workspace, logger, **params)

    def run(self, c1, c3, b4, *args, **kwargs):
        return {"d": (c1 + c3 + b4) / 4}


if __name__ == "__main__":
    a = A(produces="data")
    b1 = B(strategy="max", produces="b1", consumes="data")
    b2 = B(strategy="min", produces="b2", consumes="data")
    b3 = B(strategy="mean", produces="b3", consumes="data")
    b4 = B(strategy="sum", produces="b4", consumes="data")
    b1.depends_on.append(a)
    b2.depends_on.append(a)
    b3.depends_on.append(a)
    b4.depends_on.append(a)

    c = C(produces=["c1", "c2", "c3"], consumes=["b1", "b2", "b3"])
    c.depends_on.append(b1)
    c.depends_on.append(b2)
    c.depends_on.append(b3)

    d = D(produces="d", consumes=["c1", "c2", "c3", "b4"])
    d.depends_on.append(c)
    d.depends_on.append(b4)

    g = Graph(
        context=Context(logging_enabled=True),
        logger=setup_logger("test", filename=None),
    )
    g.add_module(a)
    g.add_module(b1)
    g.add_module(b2)
    g.add_module(b3)
    g.add_module(b4)
    g.add_module(c)
    g.add_module(d)
    g.add_dependency(a, b1)
    g.add_dependency(a, b2)
    g.add_dependency(a, b3)
    g.add_dependency(a, b4)
    g.add_dependency(b1, c)
    g.add_dependency(b2, c)
    g.add_dependency(b3, c)
    g.add_dependency(c, d)
    g.add_dependency(b4, d)

    ret = g()
    print(ret)
