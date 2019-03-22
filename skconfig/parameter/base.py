from abc import ABCMeta, abstractmethod


class Param(metaclass=ABCMeta):
    @abstractmethod
    def validate(self, param):
        ...
