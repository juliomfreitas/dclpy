# -*- coding: utf-8 -*-
from moduledef import ModuleDef
from rules import TheRule, OnlyRule, ListRule
from exception import *
from reporter import Reporter


class ModuleDefNotFound(Exception):
    pass


class _DCL(object):
    rules = ListRule()
    mods = {}
    facts = []

    # the abscence that the system founded
    resolved_absences = []

    def __init__(self):
        self.rules = ListRule()
        self.mods = {}
        self.facts = []

        self.resolved_absences = []
        self.violations = []

        # to be constructed on def init()
        self.reporter = None

    def mod(self, name_mod, *path_mods):
        self.mods[name_mod] = ModuleDef(name_mod, path_mods)

    def get_mod(self, name_mod):
        module = self.mods.get(name_mod, None)
        if not module:
            raise ModuleDefNotFound(name_mod)

        return module

    def the(self, mod_name, type_interaction, mod_target):
        self.rules.append(
            TheRule(
                self.get_mod(mod_name), 
                type_interaction, 
                self.get_mod(mod_target)
            )
        )

    def only(self, mod_name, type_interaction, mod_target):
        self.rules.append(
            OnlyRule(
                self.get_mod(mod_name), 
                type_interaction, 
                self.get_mod(mod_target)
            )
        )

    def init(self, report_file=None):
        from trace import set_listening
        set_listening()

        self.reporter = Reporter(report_file)

    def conclude(self):
        """
        Now we show the must rules not satisfied
        """
        from copy import deepcopy

        must_rules = self.rules.filter_must()
        abscences = []

        for must in must_rules:
            if must.constraint not in self.resolved_absences:
                abscences.append(must)

        if not abscences: return

        self.reporter.report(
            self.violations,
            abscences
        )

    def notify_fact(self, fact):
        rules = self.rules.filter_by_type(fact['type'])

        for rule in rules:
            try:
                rule.verify(fact)
            except DivergenceException as e:
                self.violations.append(e)
            except ResolvedAbsenceException as e:
                # stores to report on the end of the executing
                self.resolved_absences.append(e.rule)


DCL = _DCL()
