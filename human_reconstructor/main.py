import sys
import manager as mn
import test

if sys.argv.count('-vt'):
    print('Visualization Off')
elif sys.argv.count('-smpl'):
    tester = test.TestManager()
    tester.init()
    tester.run()
else:
    manager = mn.Manager()
    manager.init()
    manager.run()