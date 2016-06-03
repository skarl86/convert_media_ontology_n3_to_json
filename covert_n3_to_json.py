import json
import re
import collections
from compiler.ast import flatten

from itertools import groupby

class ParseNTriple:
    def __init__(self):
        print("ParseNTriple")

def makeTriple(line):
    reg = '(<[^\s]*>)|(_:[^\s]*)|(\".*\")'
    m = re.findall(reg, line)

    s = getMatched(m[0])
    p = getMatched(m[1])
    o = getMatched(m[2])

    return (s, p, o)

def makeTripleWithoutPrefix(line):
    s, p ,o = makeTriple(line)
    return (getObjectName(s), getObjectName(p), getObjectName(o))

def getMatched(groups):
    for g in groups:
        if g is not "":
            return g

    return ""

def excludeType(line):
    _, p, o = makeTriple(line)
    return "#type" not in p

def isVideoType(line):
    _, p, o = makeTriple(line)
    return ("#type" in p) and ("Video" in o)

def hasShot(line):
    _, p, _ = makeTriple(line)
    return "hasShot" in p
def isLabel(line):
    _, p, _ = makeTriple(line)
    return "#label" in p

def getObjectName(object):
    # reg = '([#A-Z])\w+'
    # m = re.search(reg, object)
    # if m is None:
    #     return object
    # return m.group()
    newStr = object.replace("http://data.diquest.com/ontology/", "")
    newStr = newStr.replace("<","")
    newStr = newStr.replace(">","")
    return newStr

def filterShot(line):
    s, _, _ = makeTriple(line)
    return selectedShot in s

def getObjectNameAtLine(line):
    s, p, o = makeTriple(line)
    return "\t".join([getObjectName(s), getObjectName(p), getObjectName(o)])

def getLabel(line):
    s1, p1, o1 = line.split("\t")
    labels = filter(isLabel, lines)

    for l in labels:
        s2, p2, o2 = makeTriple(l)
        if o1 is s2:
            return o2
    return "None"

def isSubjectShot(line):
    s, _, _ = makeTriple(line)
    reg = r'Video[0-9]+_Shot[0-9]+'
    m = re.findall(reg, s)
    return len(m) is not 0


def isShot(line):
    _, p, o = makeTriple(line)
    return "Shot" in o

def isLabel(line):
    _, p, _ = makeTriple(line)
    return "#label" in p

def isObject(line):
    s, _, _ = makeTripleWithoutPrefix(line)
    reg = r'Video[0-9]+_[a-z0-9]\w+'
    m = re.findall(reg, s)
    return len(m) is not 0

def isElement(line):
    s, _, _ = makeTripleWithoutPrefix(line)
    reg = r'Element[0-9]+'
    m = re.findall(reg, s)
    return len(m) is not 0

def createLabelDictionary(lines):
    labelTriple = filter(isLabel, lines)
    labelDict = {}
    for line in labelTriple:
        s, _ ,o = makeTripleWithoutPrefix(line)
        labelDict[s] = o
    return labelDict

def createShotValuesDictionary(lines):
    shotsTriples = filter(excludeType, filter(isSubjectShot, lines))
    shotDict = {}

    for line in shotsTriples:
        s, p, o = makeTripleWithoutPrefix(line)
        if s not in shotDict:
            shotDict[s] = []
        shotDict[s].append(line)

    return shotDict

def createObjectDictionary(lines):
    objectTriple = filter(isObject, lines)
    objectDic = {}
    for line in objectTriple:
        s, p, o = makeTripleWithoutPrefix(line)
        if s not in objectDic:
            objectDic[s] = []
        objectDic[s].append("\t".join([s, p, o]))

    return objectDic

def createElementDictionary(lines):
    elementTriple = filter(isElement, lines)
    elementDic = {}
    for line in elementTriple:
        s, p, o = makeTripleWithoutPrefix(line)
        if s not in elementDic:
            elementDic[s] = []
        elementDic[s].append("\t".join([s, p, o]))

    return elementDic


# orginData = open("/Users/NK/Workspace/intellij/media_ontology_browser/web/data/PM_fi.0.n3")
with open("PM_fi.0.n3") as f:
    lines = f.readlines()

labelDictionary = createLabelDictionary(lines)
shotsDictionary = createShotValuesDictionary(lines)
objectDictionary = createObjectDictionary(lines)
elementDictionary = createElementDictionary(lines)

videoAndShot = []

videoAndShotTriple = filter(hasShot, lines)

for line in videoAndShotTriple:
    s, _, o = makeTripleWithoutPrefix(line)
    videoAndShot.append((s, o))

dic = {}
selectedShot = ""

for videoID, shots in groupby(videoAndShot, lambda x: x[0]):
    print videoID

    if videoID not in dic:
        dic[videoID] = []
    shotsList = []
    shotDict = {}
    videoDict = {}
    labelDict = {}
    for shot in shots:
        temp = {}
        list = shotsDictionary[shot[1]]
        for st in list:
            _, p, o = makeTripleWithoutPrefix(st)
            if p not in temp:
                temp[p] = []
            objectDic = {}
            if o in objectDictionary:
                objectDic[o] = objectDictionary[o]
            elif o in elementDictionary:
                objectDic[o] = elementDictionary[o]

            temp[p].append(objectDic)

        shotsList.append(temp)
        shotDict[shot[1]] = shotsList

    videoDict["shots"] = shotDict
    label = "None"

    if videoID in labelDictionary:
        label = labelDictionary[videoID]
    videoDict["label"] = label
    dic[videoID] = videoDict

# for key, shots in groupby(videoAndShot, lambda x: x[0]):
#     print key
#     newKey = getObjectName(key)
#     dic[newKey] = {"label" : labelDictionary[newKey]}
#     for value in shots:
#         shotDic = {}
#         shot = getObjectName(value[1])
#         if shot not in shotDic:
#             shotDic[shot] = []
#         selectedShot = shot
#         filteredShotValues = filter(excludeType, shotValues)
#         newShotValues = [getObjectNameAtLine(v) for v in filteredShotValues]
#
#         shotDic[shot] = flatten([shotDic[shot], newShotValues])
#
#         if newKey not in dic:
#             dic[newKey] = []
#         dic[newKey].append(shotDic)
#
#
od = collections.OrderedDict(sorted(dic.items()))


with open("new_media_video3.json", "w") as outfile:
    json.dump(od,outfile,indent=2)




