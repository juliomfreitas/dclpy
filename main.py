# -*- coding: utf-8 -*-
from controller import *
from dclpy import *



class Main:
    def start_system(self):
        #c = Controller("Home")
        #c.dispatch('/')
        #c.dispatch('/aereo/')

        from a import A
        A()



if __name__ == "__main__":
    """DCL.mod('urls_publicas', 'controller')
    DCL.mod('modelos', 'models')
    DCL.mod('utilidades', 'models')

    DCL.the('urls_publicas', CantAccess, 'modelos')  
    DCL.the('urls_publicas', CantCreate, 'modelos')      
    DCL.the('urls_publicas', CantAccess, 'utilidades')
    DCL.the('modelos', CantInherit, 'modelos')
    
    DCL.only('modelos', CanAccess, 'utilidades')

    DCL.the('urls_publicas', MustCreate, 'modelos') """ 

    DCL.mod('A', 'a')
    DCL.mod('B', 'b')
    DCL.mod('C', 'c')
    DCL.mod('D', 'd')


    DCL.the('A', CantAccess, 'B')
    DCL.the('A', CantCreate, 'B')
    DCL.the('B', CantInherit, 'C')

    DCL.the('B', MustInherit, 'D')
    DCL.only('A', CanInherit, 'D')

    DCL.init(report_file='C:\\mestrado\\dclpy\\report.txt')

    a = Main().start_system()

    # TODO: abstract this. Maybe a context manager can does this
    DCL.conclude()

    print '\n\n\n'
