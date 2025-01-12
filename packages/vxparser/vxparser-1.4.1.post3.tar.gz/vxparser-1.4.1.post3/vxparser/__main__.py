import os, sys
rp = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(rp)
sys.path.append(os.path.join(rp, 'helper'))
sys.path.append(os.path.join(rp, 'utils'))
from main import main

main()
