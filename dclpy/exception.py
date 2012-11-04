
class SerializableException(Exception):
    def __init__(self, fact, message="No message"):
        self.fact = fact
        code = '  File "%s", line %s\n' % (fact['code'].co_filename, fact['code'].co_firstlineno)
        self.message = message + '\n\t' + code


class DivergenceException(SerializableException):
    """
    Exemple of rules that generates exceptions by divergence:
        * module X can't access objects from module Y
        * module X can't inherit objects from module Y
    """ 


class ResolvedAbsenceException(SerializableException):
    """
    Exemple of rules that generates exceptions by divergence:
        * module X must access objects from module Y
        * module X must inherit objects from module Y
    """ 
    def __init__(self, fact, rule, message="No message"):
        retorno = super(ResolvedAbsenceException, self).__init__(
            fact,
            message=message
        )

        # This will be compared with all the must rules, to indicate a 
        # satisfied commitment
        self.rule = rule



class ConstraintDoesNotMatchException(Exception):
    pass

    
