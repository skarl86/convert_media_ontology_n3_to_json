import re
import collections
import json
from itertools import groupby

def getMatched(groups):
    for g in groups:
        if g is not "":
            return g

    return ""



def makeTriple(line):
    reg = '(<[^\s]*>)|(_:[^\s]*)|(\".*\")'
    m = re.findall(reg, line)

    s = getMatched(m[0])
    p = getMatched(m[1])
    o = getMatched(m[2])

    return (s, p, o)

def hasShot(line):
    _, p, _ = makeTriple(line)
    return "hasShot" in p

def isVideoType(line):
    _, p, o = makeTriple(line)
    return ("#type" in p) and ("Video" in o)

with open("PM_fi.0.n3") as f:
    lines = f.readlines()

hasShotVideos = filter(hasShot, lines)
videoAndShot = []

for line in hasShotVideos:
    s, p, o = makeTriple(line)
    videoAndShot.append((s, o))

videoAndShotCount = {}
shotSum = 0.0

for videoID, shots in groupby(videoAndShot, lambda x: x[0]):
    shotsList = list(shots)
    shotSum += len(shotsList)
    videoAndShotCount[videoID] = len(shotsList)

videoCount = len(videoAndShotCount.items())

print("Total Video Count : %d" % videoCount)
print("Total Shot Count  : %d" % shotSum)
print("Average Shot per Video : %f " % (shotSum/videoCount))

od = collections.OrderedDict(sorted(videoAndShotCount.items()))

# with open("shot_count_each_video.json", "w") as outfile:
#     json.dump(od,outfile,indent=2)