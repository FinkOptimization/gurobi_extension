from abc import abstractmethod, ABC
from gurobipy import *


def _validateCallbackAndWhere(callback, where):
    if not callable(callback):
        raise RuntimeError("The argument 'callback' must be callable")
    if where is None or not isinstance(where, int):
        raise RuntimeError("The 'where' argument must be set to an integer value when providing a callback method")


class Callback(ABC):
    @property
    @abstractmethod
    def where(self):
        ...

    @where.setter
    @abstractmethod
    def where(self, value: int):
        ...

    @abstractmethod
    def callback(self, model: Model):
        ...


class CallbackWrapper(Callback):
    where = 0

    def __init__(self, callback, where, **kwargs):
        _validateCallbackAndWhere(callback, where)
        self._callback = callback
        self.where = where
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def callback(self, model: Model):
        self._callback(self, model)


def __mainCallback__(model: Model, where: int):
    if where in model._callbacks:
        for cb in model._callbacks[where]:
            cb.callback(model)


class Model(Model):
    _callbacks = {}

    def addCallback(self, callback, where=None, **kwargs) -> Callback:
        if isinstance(callback, Callback):
            cb = callback
        else:
            _validateCallbackAndWhere(callback, where)
            cb = CallbackWrapper(callback, where, **kwargs)

        if cb.where not in self._callbacks:
            self._callbacks[cb.where] = []

        self._callbacks[cb.where].append(cb)

        return cb

    def removeCallback(self, callback: Callback):
        self._callbacks[callback.where].remove(callback)

    def clearCallbacks(self):
        self._callbacks = {}

    def optimize(self):
        if len(self._callbacks) > 0 and any(len(cb) > 0 for _, cb in self._callbacks.items()):
            super().optimize(__mainCallback__)
        else:
            super().optimize()
