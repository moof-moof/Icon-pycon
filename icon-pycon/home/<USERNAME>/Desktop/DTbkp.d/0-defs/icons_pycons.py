
""" A pair of function definitions for saving and restoring the preferred positions
of the set of all desktop icons.

Hopefully useful in case one's handcrafted desktop layout has been 
accidentally deleted, e.g. by clicking the inexplicable contextual menu 
option "Organize desktop by name", which of course can't be undone...

Names of icons' corresponding files must have no leading or trailing spaces.

Tested on Ubuntu Mate 20.04, using the Caja file manager and python3. 
Requires gio and egrep.


Based on a rather more elaborate script provided by RockDoctor 
(https://www.linuxquestions.org/questions/attachment.php?attachmentid=35284&d=1610746200)

By moof-moof 2021-01-20 (https://github.com/moof-moof?tab=repositories).

"""


import os, sys, subprocess, pickle
from datetime import date

home = os.getenv("HOME")                  # home/<user> dir
desktop = home + '/<Desktop>/'            # Provide your localized DT name here
pname = desktop + '<dir>/Icons_ervator.p' # Pickle file (dir name to suit)
td = date.today().isoformat()             # YYYY-MM-DD format
dpname = pname + '-' + td                 # Pickle file with date suffix

# home = os.getenv("HOME")                    # /home/xneb
# desktop = home + '/Skrivbord/'              # /home/xneb/Skrivbord/
# pname = desktop + 'DTbkp.d/Icons_ervator.p' # /home/xneb/Skrivbord/DTbkp.d/Icons_ervator.p
# td = date.today().isoformat()               # YYYY-MM-DD
# dpname = pname + '-' + td                   # /home/xneb/Skrivbord/DTbkp.d/Icons_ervator.db-YYYY-MM-DD

gio_in_cmd = "gio info $HOME/Skrivbord/* | egrep 'standard::name|caja-icon-position:'"

savedPositions = []
currentPositions = []  

# ---------------------------------------------------------------------#


def SAVE_current_layout():

    positions = []

    p = subprocess.Popen(gio_in_cmd, shell=True, bufsize=4096, stdout=subprocess.PIPE).stdout
    line = p.readline().strip().decode('unicode_escape').encode('latin-1').decode('utf8')

    while line:
        name = line[16:]                    ## Line-pos 1 (name)
        line = p.readline().strip().decode('unicode_escape').encode('latin-1').decode('utf8')
        
        line = line[30:]                    ## Line-pos 2 (coords)
        temp = line.split(",")              ## Line-pos 2a, 2b (x, y)
        try:
            positions.append([name, int(temp[0]), int(temp[1])])
        except:
            print("Choked on this one: ", name)
            print(temp)
            sys.exit(148)
        line = p.readline().strip().decode('unicode_escape').encode('latin-1').decode('utf8')

    currentPositions = positions[:]
    print(positions)

    with open(dpname, 'wb') as f:
        pickle.dump(currentPositions, f)    ## Puts everything in storage
        f.close()

    print("\n     <====================<  DONE! >=====================> ")



# ---------------------------------------------------------------------#


def RESTORE_saved_layout():
    
    print("\n        busy... busy.. busy.. ")

    with open(pname, 'rb') as f:
        savedPositions = pickle.load(f)     ## Reads from pickled file
        f.close()

    for p in savedPositions:
        icon = desktop + p[0]
        xy = str(p[1]) + "," + str(p[2])
        gio_out_cmd = ["gio", "set", icon, 'metadata::caja-icon-position', xy]
        subprocess.run(args=gio_out_cmd)    ## Puts everything back again!

    print("\n<------------------------- Done! ----------------------------->")
    print("          Time to refresh Caja (with the F5 routine)")



# ---------------------------------------------------------------------#
##   Finally, to refresh the desktop simply hit F5 while "touching" the
##   desktop with the pointer. That's the passive-aggressive way.
##
##   To more aggressively restart caja run in separate terminal: 
##      caja -q && caja -n &
##
##   or even more violently:
##      killall -9 caja (Oy Gevald!)
# ---------------------------------------------------------------------#
