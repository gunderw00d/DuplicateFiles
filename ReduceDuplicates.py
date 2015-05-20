import os
import functools
import shutil
import win32api

imageExts = {'.jpg', '.jpeg', '.cr2', '.nef', '.gif', '.tif', '.tiff', '.png', '.bmp', '.psd', '.ppm'}
mainDict = {}       # {fileName: list(paths file name found in) }
#extensions = {}
extCount = {}

def CatalogFiles(path):
    dirContents = os.listdir(path)   # Get list of items in the current dir.
    for d in dirContents:
        if d != "AppData":
            newPath = win32api.GetShortPathName(os.path.join(path, d))
            if os.path.isdir(newPath):
                #print("+  " + newPath)
                CatalogFiles(newPath)
            else:
                fileExt = os.path.splitext(d)
                if len(fileExt) == 2:
                    extLower = fileExt[1].lower()
                    if extLower in imageExts:
                        #print(" I " + newPath)
                        tmpList = mainDict[d] = mainDict.get(d, list())
                        tmpList.append(newPath)
                        extCount[extLower] = extCount.get(extLower, 0) + 1
                    #else:
                    #    print("   " + newPath)


fnameSizeDict = {}   # {fileName: {size: list(paths file of that name and size found in) } }

def PrintSizeStats():
    moreThanOneSize = 0
    noAccess = 0
    badAccess = 0
    numLens = {}
    for file, sizePaths in fnameSizeDict.items():
        numSizes = len(sizePaths.keys())
        if numSizes > 1:
            moreThanOneSize += 1
            numLens[numSizes] = numLens.get(numSizes, 0) + 1
            if numSizes > 4:
                print(str(numSizes) + ": " + file)
        if -1 in sizePaths.keys():
            noAccess += 1
        if -2 in sizePaths.keys():
            badAccess += 1

    print("     " + str(moreThanOneSize) + " files with more than 1 filesize.")
    print("     " + str(noAccess) + " files with no access permissions")
    print("     " + str(badAccess) + " files with BAD access permissions")
    print(numLens)
    print(extCount)


def ReSortBySize():
    for file, pathList in mainDict.items():
        sizes = {}
        for path in pathList:
            sz = -1
            if os.access(path, os.R_OK):
                try:
                    statInfo = os.stat(path)
                    sz = statInfo.st_size
                except OSError:
                    sz = -2
            tmpList = sizes[sz] = sizes.get(sz, list())
            tmpList.append(path)
        fnameSizeDict[file] = sizes
    #PrintSizeStats()


def PickSingleSrcTarget(pathList):
    #print(pathList)
    # pick the best src dir and create a target dir, put into a list.
    cutOffDirs = [ 'photography', 'desktop', 'pictures']
    outputBase = 'E:\\Unique\\Pictures'
        
    bestPathIndex = 0     # TODO
    path = win32api.GetLongPathName(pathList[bestPathIndex])
    #print(path)
    
    pathComponents = path.split('\\')
    #print(pathComponents)

    cutOffIndex = -1
    for i in range(len(pathComponents)):
        if pathComponents[i].lower() in cutOffDirs:
            cutOffIndex = i
            break
    #print(i)
    if cutOffIndex >= 0:
        #print(pathComponents[i+1:])
        foo = functools.reduce(os.path.join, pathComponents[i+1:])
        foo = os.path.join(outputBase, foo)
        #print(foo)
        bar = [path, foo]
        print(bar)
    else:
        print("  -- no cutoff dir for path: " + path)

    
    #subPath = functools.reduce(os.path.join, pathComponents[2:])

    #return []

#fnameSizeDict = {}   # {fileName: {size: list(paths file of that name and size found in) } }    
# {fileName: [(src -> dest), ...] }
#   only one file size, just pick first path for source.
#       dest -->  hrmm... where to chop that first path off.
#       Photography, Desktop, Pictures

#fnameCopyInfo = {}    # { fileName: [ [src, dest], ...] }
#def GenerateCopyInfo():
#    for fileName, sizePathsDict in fnameSizeDict:
#        if len(sizePathsDict.keys()) == 1:
#            fnameCopyInfo[fileName] = PickSingleSrcTarget(sizePathsDict.keys())


# find all image files and collect their paths - look for duplicate file names and see if we can figure out what's
# an actual duplicate vs. a coincidence.
pathBase=["E:\\2TB_Drive"]#, "E:\\2TB_JanBackup", "E:\\4TB_Backup", "E:\\C_Drive", "E:\\Seagate Dashboard 2.0"]

for path in pathBase:
    CatalogFiles(win32api.GetShortPathName(path))


count = 0
for k in mainDict.keys():
    count += len(mainDict[k])
#print("  " + str(sum))

print(str(len(mainDict.keys())) + " files in " + str(count) + " paths")

ReSortBySize()


# TODO -- this works on a single entry - scale up to multiple
fnameList = list(fnameSizeDict.keys())
sizePathsDict = fnameSizeDict[fnameList[0]]
pathList = list(sizePathsDict.values())
PickSingleSrcTarget(pathList[0])

##bar = ['E:\\2TB_DR~1\\SONYBA~1\\HDD1\\ALLUSE~1\\Adobe\\PHOTOS~1\\8.0\\PHOTOC~1\\frames\\CO60DE~1.JPG']
##PickSingleSrcTarget(bar)



# everything with one file size and multiple locations
#    check locations - all parallel?  copy once to similar folder
#                      multiple paths? copy to each dissimilar folder and note in log
#   more than one file size?
#      a size has more than one path?  same treatment - folders similar, copy once, dissimilar, copy and note
#      size dest path already exists?  rename and copy to existing location.

#  Maybe stop after 5 file sizes - rest seem to be outliers.  Dump their loc and check manually.





#extens = []
#extens.extend(extensions.keys())
#extens.sort()
#for ext in extens:
#    print(ext)

copyCommands = []
mkdirsCommands = []

def GenerateCommands():
    uniqueFileBase='Unique'
    for fileName, pathList in mainDict.items():
        newCopies = {}
        for path in pathList:
            pathComponents = path.split('\\')
            subPath = functools.reduce(os.path.join, pathComponents[2:])
            if subPath not in newCopies.keys():
                targetLoc = os.path.join(uniqueFileBase, subPath)
                newCopies[subPath] = [path, targetLoc]
        copyCommands.extend(newCopies.values())

    # generate a set of mkdir commands off the copy commnads
    fooBar = {}
    for cpCmd in copyCommands:
        prefix, filename = os.path.split(cpCmd[1])
        if prefix not in fooBar.keys():
                fooBar[prefix] = 1

    mkdirsCommands.extend(fooBar.keys())
    mkdirsCommands.sort()


def ExecuteCommands():
    for dirPath in mkdirsCommands:
        print("os.makedirs('" + dirPath + "')")
        os.makedirs(dirPath)

    for cpPaths in copyCommands:
        print("shutil.copy2('" + cpPaths[0] + "', '" + cpPaths[1] + "')")
        shutil.copy2(cpPaths[0], cpPaths[1])

