
from b import B, ClassB


def A():
    print 'EXECUTANDO A'
    print 'VOU CHAMAR O B AGORA'
    B()
    print 'VOU INSTANCIAR CLASSE DE B AGORA'
    b = ClassB()
    print 'PRONTO'




