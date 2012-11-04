# -*- coding: utf-8 -*-
DEBUG = True


class Reporter(object):
    """
    Centralizes report with user
    """
    def __init__(self, foutput=None):
        import sys

        self.output = []
        if not foutput or DEBUG:
            self.output.append(sys.stdout)
        
        if foutput:
            self.output.append(open(foutput, 'w'))

    def report(self, violations, abscences):

        for media in self.output:
            self.print_to(media, violations, abscences)


    def print_to(self, media, violations, abscences):
        """
        TODO: template engine
        """
        print >>media, 'X' * 79
        print >>media, "dclpy: architectural verification tool"
        print >>media, ''
        print >>media, 'monitoring from %s to %s (%d minutes)' % (
            '2012-02-01 12:00', '2012-02-01 14:00', 120
        )
        print >>media, '-' * 79
        print >>media, ''        

        print >>media, 'Arquitectural Violations'
        print >>media, '########################\n'

        for x in violations:
            print >>media, x.message

        print >>media, 'Arquitectural Absences'
        print >>media, '######################\n'

        for exp in abscences:
            print >>media, exp.constraint
            print >>media, ''

        print >>media, '-' * 79
        print >>media, ''
        print >>media, 'Total: %d violation(s) and %d abscence(s)' %(
            len(violations), len(abscences)
        )            

        if violations or abscences:
            print >>media, 'Good luck in improving your system!'            
        else:
            print >>media, 'Congratulations! We didn\'t detect any fault'

        print >>media, ''
        print >>media, 'End of Report.'
        print >>media, ''
        print >>media, 'X' * 79
