# -*- coding: utf-8 -*-
from statemachine import DCL

###############################################################################
# Logging


class FrameHandler(object):
    """
    Handle the execution frame, abstracting all information necessary to 
    extract a fact 
    """
    def __init__(self, frame, event):
        self._frame = frame
        self._local_env = frame.f_locals
        self._event = event

    def __bool__(self):
        """
        For us, is only valid the frames related with functions calls
        """
        return self._event == 'call'

    def get_module(self):
        return self._frame.f_code.co_filename

    def get_object(self):
        return self._local_env.get('self', None)

    def get_function_name(self):
        return self._frame.f_code.co_name

    def get_last_frame(self):
        return FrameHandler(self._frame.f_back, self._event)
     

    def __str__(self):
        objeto = self.object()
        nome_funcao = self.function_name

        modulo = None
        if objeto:
            modulo = objeto.__module__

        if not modulo:           
            modulo = self._local_env.get('__package__', '') or ''
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


class FactExtractor(object):
    """
    Given a captured Frame, tryies to obtain a fact to be validated by
    the system
    """
    def __init__(self, dclframe):
        self.frame = dclframe

    def notify_facts(self):
        """
        Search every fact that can be extracted in the received frame and
        notifyies the app about the found facts
        """
        frame = self.frame

        if frame:
            called_func = frame.function_name

            if called_func == '__init__':
                self.notify_new_object(
                    frame.last_frame.object, 
                    frame.object.__class__,
                    called_func
                )

                bases = frame.object.__class__.__bases__

                # object is the default inheritance, so we don't need it
                bases = filter(lambda x: x != object, bases)

                # TODO: it ain't the best way to do that, because this notification 
                # is going to be lauched more times thant we need
                self.notify_inheritance(
                    bases, frame.object.__class__
                )
            else:
                self.notify_function_call(
                    frame.last_frame.object,
                    frame.object,
                    called_func
                )

    # FIXME: For awhile, we will ignore args and kwargs of functions
    def notify_new_object(self, sender, cls, method_name):
        #print 'New object ', sender, ' created by ', cls
        fact = {'type': 'objcreation', 
                'sender': sender.__class__, # or 'Main', 
                'cls': cls}
                
        DCL.notify_fact(fact)

    def notify_inheritance(self, parents, subclass):
        #    print 'Inheritance ', subclass, ' of class ', parent

        # NOTE: python has multiple inheritance
        for parent in parents:
            fact = {'type': 'inheritance', 
                    'parent': parent, 
                    'cls': subclass}

            DCL.notify_fact(fact)            

    def notify_function_call(self, sender, obj, method_name):
        #print 'Func call ', method_name, ' of object ', (obj or 'Main'), ' by ', (sender or 'Main')

        fact = {'type': 'methodcall', 
                'sender': sender.__class__, 
                'object': obj.__class__, # or 'Main',
                'method': method_name}

        DCL.notify_fact(fact)        


def set_listening():
    def listener(frame, event, arg, **kwargs):
        # DEBUG PARA CAPTURAR DADOS DO FRAME ATUAL  
        #print dir(frame)
        #for x in dir(frame.f_code):
        #    print "%s = <%s>" % (x, getattr(frame.f_code, x))

        # PRETTY PRINT IMPORTANTE PARA WINDOWS
        #import pprint
        #pp = pprint.PrettyPrinter(indent=4)

        #import inspect
        #pp.pprint(inspect.getmembers(objeto))
        #pp.pprint(objeto)
        
        #pp.pprint(dir(objeto.__class__))
        #pp.pprint(traceback.extract_stack())

        fact = FactExtractor(FrameHandler(frame, event))
        fact.notify_facts()

        if event == 'call':
            #print frame, arg, kwargs
            #print "F: %s, \n\tANTERIOR: %s\n" % (dclframe, dclframe.last_frame())
            pass

        return listener

    import sys
    sys.settrace(listener)
