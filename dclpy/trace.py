# -*- coding: utf-8 -*-
"""
Características importantes

* Ele não passa por código builtin. Por exemplo se a clase não implementar 
__init__ não vamos conseguir rastrear
* Código em thread funciona, porque o uso de sys.settrace() é especifico
à thread executada no momento, não é global
* Depende muito da implementação, é necessário validar entre muitas 
implementações de python. Atualmente funciona em cPython

"""
from statemachine import DCL

###############################################################################
# Logging


class FrameHandler(object):
    """
    Handle the execution frame, abstracting all information necessary to 
    extract a fact 

    Atriubutos de um objeto frame: 
        f_back  next outer frame object (this frame’s caller)    
        f_builtins  builtins namespace seen by this frame    
        f_code  code object being executed in this frame     
        f_exc_traceback traceback if raised in this frame, or None   
        f_exc_type  exception type if raised in this frame, or None  
        f_exc_value exception value if raised in this frame, or None     
        f_globals   global namespace seen by this frame  
        f_lasti index of last attempted instruction in bytecode  
        f_lineno    current line number in Python source code    
        f_locals    local namespace seen by this frame   
        f_restricted    0 or 1 if frame is in restricted execution mode  
        f_trace tracing function for this frame, or None         

    Atributos de um objeto de codigo (frame._f_code)
        co_argcount number of arguments (not including * or ** args)     
        co_code string of raw compiled bytecode  
        co_consts   tuple of constants used in the bytecode  
        co_filename name of file in which this code object was created   
        co_firstlineno  number of first line in Python source code   
        co_flags    bitmap: 1=optimized | 2=newlocals | 4=*arg | 8=**arg     
        co_lnotab   encoded mapping of line numbers to bytecode indices  
        co_name name with which this code object was defined     
        co_names    tuple of names of local variables    
        co_nlocals  number of local variables    
        co_stacksize    virtual machine stack space required     
        co_varnames tuple of names of arguments and local variables     


    Links que podem ser uteis
    http://farmdev.com/src/secrets/framehack/index.html#exploring-frame-objects
    http://docs.python.org/2/library/inspect.html
    http://www.doughellmann.com/PyMOTW/sys/tracing.html
    
    """
    def __init__(self, frame, event):
        self._frame = frame
        #self._local_env = frame.f_locals
        self._event = event

    def __bool__(self):
        """
        For us, is only valid the frames related with functions calls
        """
        return True
        return self._event == 'call'

    def get_module(self):
        return self._frame.f_code.co_filename

    def get_object(self):
        if self._frame.f_locals:
            return self._frame.f_locals.get('self', None)
        else:
            return None

    def get_function_name(self):
        return self._frame.f_code.co_name

    def get_last_frame(self):
        return FrameHandler(self._frame.f_back, self._event)
     
    def get_code(self):
        return self._frame.f_code

    def __str__(self):
        objeto = self.object
        nome_funcao = self.function_name

        modulo = None
        if objeto:
            modulo = objeto.__module__

        if not modulo:           
            modulo = self._frame.f_locals.get('__package__', '') or ''
            modulo += __file__.split('.')[0] or ''
            # outra maneira:
            # >modulo = self.module()

        return "*\t modulo: %(modulo)s, objeto: %(objeto)s, funcao: %(fn)s" % {
            'modulo': modulo,
            'objeto': objeto.__class__.__name__ if objeto else modulo,
            'fn': nome_funcao
        }

    module = property(get_module)
    object = property(get_object)
    function_name = property(get_function_name)
    last_frame = property(get_last_frame)
    code = property(get_code)


DEBUG = False

class FactExtractor(object):
    """
    Given a captured Frame, tryies to obtain a fact to be validated by
    the system
    """
    def __init__(self, frame, event):
        self.frame = frame
        self.event = event

    def notify_facts(self):
        """
        Search every fact that can be extracted in the received frame and
        notifyies the app about the found facts
        """
        import inspect

        actualframe = self.frame
        bytecode_actualframe = actualframe.f_code

        lastframe = actualframe.f_back
        bytecode_lastframe = lastframe.f_code

        # Performance
        if self.event == 'line': return

        # If we were returning from a __init__ function, it means:
        #  1 - We're creating an object
        #  2 - by PEP, there's a self object so we can find his base classes
        # NOTE: co_name is the name of the function will be executed on 
        # the next frame
        if self.event == 'return' and bytecode_actualframe.co_name == '__init__':
            self.notify_new_object(
                # modulo que chamou a função 
                bytecode_lastframe.co_filename, 
                # Classe instanciada
                bytecode_actualframe.co_filename,
                bytecode_lastframe
            )

            obj = actualframe.f_locals['self'].__class__

            bases = filter(lambda x: x != object, obj.__bases__)
            bases = map(inspect.getsourcefile, bases)
            
            self.notify_inheritance(
                bases, 
                inspect.getsourcefile(obj), 
                bytecode_lastframe
            )


            if DEBUG:
                print 'X' * 79
                print 'CRIACAO DE OBJETO \n'
                print '\tModulo que criou o objeto: ', bytecode_lastframe.co_filename
                print '\tModulo de classe instanciada: ', bytecode_actualframe.co_filename
                print 'X' * 79
                print 

        elif self.event == 'call' and bytecode_actualframe.co_name != '__init__':
            # co_name == nome da função que sera executada no proximo            
            self.notify_function_call(
                # modulo que chamou a função 
                bytecode_lastframe.co_filename, 
                # modulo que esta sendo executado
                bytecode_actualframe.co_filename,                
                # nome da função executada
                bytecode_actualframe.co_name, 
                # bytecode da função sendo executada
                bytecode_lastframe
            )

            if DEBUG:
                def pprint(f):
                    obj_codigo = f.f_code
                    print '\tModulo em questão: ', obj_codigo.co_filename
                    print '\tNome da função', obj_codigo.co_name
                    print '\tNumero da Linha', f.f_lineno


                print 'X' * 79
                print 'CHAMADA DE FUNCAO \n'
                print 'FRAME ATUAL'
                pprint(actualframe)
                print 'FRAME ANTERIOR'            
                pprint(lastframe)
                print 'X' * 79
                print 


        return 

        """
        local_object = None

        if frame.f_locals:
            local_object = frame.f_locals.get('self', None)   


        for m in ['logging', 'sre_parse', 'Cookie', 'socket', 
                  'wsgiref', 'dclpy', 'pdb', 'sys']:
            try:
                if local_object.__class__.__module__.find(m) != -1:
                    print '>>>>Esse frame nao vai ser considerado por ser de modulo %s' % frame.object.__class__.__module__
                    return
            except RuntimeError, e:
                print '>>>>Esse frame nao vai ser considerado por RuntimeError %s' % frame.object.__class__.__module__                
                # XXX Occurs and recursion limit error on SimpleLazyObject for
                # user that we cant understand yet
                return
        """


        if frame:


            called_func = frame.f_code.co_name



            if called_func == '__init__':
                self.notify_new_object(
                    last_frame.object, 
                    local_object.__class__,
                    called_func,
                    bytecode
                )

                bases = frame.object.__class__.__bases__

                # object is the default inheritance, so we don't need it
                bases = filter(lambda x: x != object, bases)

                # TODO: it ain't the best way to do that, because this notification 
                # is going to be lauched more times thant we need
                self.notify_inheritance(
                    bases, frame.object.__class__, frame.code
                )
            else:
                self.notify_function_call(
                    last_frame.object,
                    frame.object,
                    called_func,
                    bytecode
                )

        print 
        print 

    # FIXME: For awhile, we will ignore args and kwargs of functions
    def notify_new_object(self, sender, cls, code):
        #print 'New object ', sender, ' created by ', cls
        fact = {'type': 'objcreation', 
                'sender': sender, # or 'Main', 
                'receiver': cls,
                'code': code}
                
        DCL.notify_fact(fact)

    def notify_inheritance(self, parents, subclass, code):
        #    print 'Inheritance ', subclass, ' of class ', parent

        # NOTE: python has multiple inheritance
        for parent in parents:
            fact = {'type': 'inheritance', 
                    'sender': parent, 
                    'receiver': subclass,
                    'code': code}

            DCL.notify_fact(fact)            

    def notify_function_call(self, sender, obj, method_name, code):
        #print 'Func call ', method_name, ' of object ', (obj or 'Main'), ' by ', (sender or 'Main')

        fact = {'type': 'methodcall', 
                'sender': sender, 
                'receiver': obj, # or 'Main',
                'method': method_name,
                'code': code}

        #print fact
        DCL.notify_fact(fact)        


def set_listening():
    import sys

    def listener(frame, event, arg, **kwargs):
        # CALL a cada chamada de metodo não builtin
        # LINE a cada nova linha executada
        fact = FactExtractor(frame, event)
        fact.notify_facts()

        return listener

    sys.settrace(listener)

