import os.path as op


directory = '/Applications/packages/E-MEG/input/stims/Exp1/'

with open(op.join(directory, 'Exp1_stimuli.csv')) as FILE:
    header = FILE.readline().strip()
    header = header.split(',')
    doc = FILE.readlines()

doc = [line.strip().split(',') for line in doc]
trials = zip(*doc)
# format primes
idx = header.index('prime')
trials[idx] = [word.lower() for word in trials[idx]]
# format target
idx = header.index('target') 
trials[idx] = [word.lower() if word != 'Incorrect' else word.upper()
               for word in trials[idx] ]
# format post
idx = header.index('post')
trials[idx] = [word.lower() if word != 'Incorrect' else word.upper()
               for word in trials[idx] ]
# remove blank
idx = header.index('blank')
header.pop(idx)
trials.pop(idx)

list1 = [header]
list1.extend(zip(*trials)[::4])
list1.extend(zip(*trials)[3::4])

list2 = [header]
list2.extend(zip(*trials)[1::4])
list2.extend(zip(*trials)[2::4])

with open(op.join(directory, 'List1.txt'), 'w') as TARGET1:
    for sentence in list1:
        sentence = '\t'.join(sentence) + "\n"
        TARGET1.write(sentence)

with open(op.join(directory, 'List2.txt'), 'w') as TARGET2:
    for sentence in list2:
        sentence = '\t'.join(sentence) + "\n"
        TARGET2.write(sentence)