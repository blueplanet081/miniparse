import sys
import miniparse as mp

mp.partial_mode = mp.PARTIAL
mp.error_code = 1

myops = {'a': mp.Oset(False, False, 'comment for a'),
         'L': mp.Oset(False, True, 'Lのコメント'),
         'f': mp.Oset(False, False, 'これがfです'),
         'l': mp.Oset(False, False, 'これがlです'),
         'verbose': mp.Oset(False, True, '静かにね'),
         }

mp.printOset(myops)

myArgs = mp.Args(sys.argv)
print('command = ', myArgs.getCommandPath())

while not myArgs.isAllEnd():
    err = mp.miniparse(myArgs, myops)

    mp.printOset(myops)
    print(myArgs.remainArgs())

for i, p in enumerate(mp.params()):
    print(i, p)
