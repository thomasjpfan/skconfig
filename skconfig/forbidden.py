from abc import ABCMeta, abstractmethod
from .exceptions import ForbiddenValue


class ForbiddenClause(metaclass=ABCMeta):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    @abstractmethod
    def is_forbidden(self, **kwargs):
        ...

    def __and__(self, other):
        return ForbiddenAnd([self, other])

    def __repr__(self):
        return "{self.__class__.__name__}: {self.name}, {self.value}".format(
            self=self)


class ForbiddenIn(ForbiddenClause):
    def is_forbidden(self, **kwargs):
        value = kwargs.get(self.name)
        if value is None:
            return
        if value in self.value:
            raise ForbiddenValue(self.name, value)


class ForbiddenEquals(ForbiddenClause):
    def is_forbidden(self, **kwargs):
        value = kwargs.get(self.name)
        if value is None:
            return
        if value == self.value:
            raise ForbiddenValue(self.name, value)


class ForbiddenAnd(ForbiddenClause):
    def __init__(self, forbidden_clauses):
        self.forbidden_clauses = forbidden_clauses

    def is_forbidden(self, **kwargs):
        names = []
        values = []
        for for_clauses in self.forbidden_clauses:
            value = kwargs.get(for_clauses.name)
            if value is None:
                return
            try:
                for_clauses.is_forbidden(**kwargs)
            except ForbiddenValue:
                names.append(for_clauses.name)
                values.append(for_clauses.value)

        if len(names) == len(self.forbidden_clauses):
            names_str = " and ".join(names)
            values_str = " and ".join(str(v) for v in values)
            raise ForbiddenValue(names_str, values_str)

    def __repr__(self):
        names = []
        for clause in self.forbidden_clauses:
            names.append(str(clause))
        return "ForbiddenAnd: ({})".format(", ".join(names))
