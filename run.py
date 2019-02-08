import sys
from modules.gen_xpath import main as gen_xpath

### READS DEFAULT JSON OR DRAG-DROPPED FILE AND RUN SCRIPT

config = ("config.json" if (len(sys.argv) == 1) else sys.argv[1])
gen_xpath(config)

input("Press any key to continue...")