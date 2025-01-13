# -*- coding: utf-8 -*-

"""package benutils
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2020-2025
license   GPL v3.0+
brief     Summator with configurable input number
"""

import logging
import signalslot as ss


class Input:

    in_updated = ss.Signal(['value'])

    def __init__(self, value=0.0):
        self._value = value

    def reset(self):
        self._value = 0.0

    def get_value(self):
        return self._value

    def set_value(self, value, **kwargs):
        self._value = float(value)
        self.in_updated.emit(value=value)


class Summator:

    out_updated = ss.Signal(['value'])

    def __init__(self, values: list[float| None]) -> None:
        assert len(values) >= 2, "must be upper or equal to 2"
        self._default_values = values
        self._inputs = list()
        self._output = 0
        self.out_updated = ss.Signal(['value'])
        for i in range(len(values)):
            if values[i] is not None:
                self._add_input(values[i])
            else:
                self._add_input(0.0)
        self._process()
        logging.debug("Summator initialized %r", self)

    def reset(self) -> None:
        for idx, inp in enumerate(self._inputs):
            if self._default_values[idx] is not None:
                inp.set_value(self._default_values[idx])
        self._process()

    def _add_input(self, value: float) -> None:
        input_ = Input(value)
        self._inputs.append(input_)
        self._inputs[-1].in_updated.connect(self._process)

    def _process(self, **kwargs) -> float:
        sum_ = 0.0
        for inp in self._inputs:
            sum_ += inp.get_value()
        self.out_updated.emit(value=sum_)
        self._output = sum_
        return sum_

    def get_output(self) -> float:
        return self._output

    def input_(self, idx: int) -> Input:
        assert idx < len(self._inputs), "index out of range"
        return self._inputs[idx]

    def set_input_value(self, idx: int, value: float) -> None:
        assert idx < len(self._inputs), "index out of range"
        self._inputs[idx].set_value(value)
        self._process()


class Summator2:

    out_updated = ss.Signal(['value'])

    def __init__(self, v0=0.0, v1=0.0):
        self._default_values = [v0, v1]
        self._inp0 = v0
        self._inp1 = v1
        self._sum = self._inp0 + self._inp1
        logging.debug("Summator initialized %r", self)

    def reset(self):
        self._inp0 = self._default_values[0]
        self._inp1 = self._default_values[1]
        self._sum = self._inp0 + self._inp1

    def process(self, **kwargs):
        self._sum = self._inp0 + self._inp1

        self.out_updated.emit(value=self._sum)
        return self._sum

    def set_inp0(self, value, **kwargs):
        self._inp0 = value
        self.process()

    def set_inp1(self, value, **kwargs):
        self._inp1 = value
        self.process()
