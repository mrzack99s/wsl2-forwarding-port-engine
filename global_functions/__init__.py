import json

def writeFile(homeDir, tasks):
    f = open(homeDir + '\\.wfp-engine\\.wfp-routines.json', 'w')
    json.dump(tasks,f, indent=3)
    f.close()
