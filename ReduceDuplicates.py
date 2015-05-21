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
    # want a dict of {destPath: [[source, destName], ... ]} for copy locations
    # so return [destPath, [source, destName]]

    cutOffDirs = [ 'photography', 'desktop', 'pictures']
    outputBase = 'E:\\Unique\\Pictures'
        
    bestPathIndex = 0     # TODO
    path = win32api.GetLongPathName(pathList[bestPathIndex])
    
    pathComponents = path.split('\\')
    #print(pathComponents)

    cutOffIndex = -1
    for i in range(len(pathComponents)):
        if pathComponents[i].lower() in cutOffDirs:
            cutOffIndex = i
            break

    if cutOffIndex >= 0:
        minLenForExtraPath = i + 2    # MAGICK NUMBER -- +1 to convert index to len, + 1 for file name.
        if len(pathComponents) > minLenForExtraPath:
            fullDestPath = functools.reduce(os.path.join, pathComponents[i+1:-1])
            fullDestPath = os.path.join(outputBase, fullDestPath)
        else:
            fullDestPath = outputBase

        bar = [fullDestPath, path]
        #print(bar)
        return bar
    else:
        #print("  -- no cutoff dir for path: " + path)
        return None


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
pathBase=["E:\\2TB_Drive", "E:\\2TB_JanBackup", "E:\\4TB_Backup", "E:\\C_Drive", "E:\\Seagate Dashboard 2.0"]

filesWithNoCutoffDir = 'Unique\\NoCutoffDir.txt'
mainCopyLog = 'Unique\\MainLog.txt'

noCutoff_file = open(filesWithNoCutoffDir, 'w')
mainLog_file = open(mainCopyLog, 'w')

print("looking for pictures...")
for path in pathBase:
    print("    checking " + path)
    CatalogFiles(win32api.GetShortPathName(path))


count = 0
for k in mainDict.keys():
    count += len(mainDict[k])

mainLog_file.write(str(len(mainDict.keys())) + " files in " + str(count) + " paths\n")

print("Found " + str(len(mainDict.keys())) + " files in " + str(count) + " paths")
print("Sorting by file size...")
ReSortBySize()

# have a dict of {fname: {size: [location, ...]} }
# want a dict of {destPath: [[source, destName], ... ]} for copy locations

# for each fname:
#    for each size:
#       pick first location & chop back to cutoff point.
#       if no cutoff path - log and skip
#
#       create dest location
#       if dest in list already:
#          change dest name and add to list of copy source/destNames

print("Discovering destinations...")
copyInfoDict = {}   # {destPath: [[source, destName], ... ]}
numNoCutoff = 0
for fname, sizeLocsDict in fnameSizeDict.items():
    dupCount = 1
    for sz, locs in sizeLocsDict.items():
        if len(locs) == 0:
            # TODO -- log
            continue
        retV = PickSingleSrcTarget(locs)
        if retV == None:
            noCutoff_file.write("  No cutoff dir in path for: " + fname + "\n")
            numNoCutoff += 1
        else:
            #print(retV)  # [destPath, sourceFullFilePath]
            destPath = retV[0]
            srcFullPath = retV[1]
            destFileName = fname
            
            tmpList = copyInfoDict[destPath] = copyInfoDict.get(destPath, list())
            if len(tmpList) > 0:
                fileBase, ext = os.path.splitext(destFileName)
                fileBase = fileBase + ' ' + str(dupCount)
                dupCount += 1
                destFileName = fileBase + ext
            tmpList.append([srcFullPath, destFileName])


print("Creating missing destination folders...")
for dp, srcFnameList in copyInfoDict.items():
    pathComponents = dp.split('\\')
    #print(pathComponents)
    #print('\nChanging to: ' + pathComponents[0] + '\\')
    os.chdir(pathComponents[0] + '\\')  # first slot should be the drive - have to include the \ to be sure we CD back to the top level dir
    createdPath = pathComponents[0]
    for pc in pathComponents[1:]:
        createdPath = os.path.join(createdPath, pc)
        if os.path.exists(pc) == False:
            mainLog_file.write('making directory ' + createdPath + '\n')
            os.mkdir(pc)
        #print('  changing to: ' + pc)
        os.chdir(pc)

os.chdir('E:\\')        # HACK - jump back up to the top level dir
    
print("Copying files...")



Intentionally broken -- fix the note below
#  Permission denied on a file
#   Add code to test if dest file exists - if so, skip copy
#   Should be able to pick up where we left off nicely.

copyCount = 0
for dp, srcFnameList in copyInfoDict.items():
    for srcFname in srcFnameList:
        mainLog_file.write('copy ' + srcFname[0] + ' ' + os.path.join(dp, srcFname[1]) + '\n')
        shortSrcName = win32api.GetShortPathName(srcFname[0])
        shortDestName = os.path.join(win32api.GetShortPathName(dp), srcFname[1])
        shutil.copy2(shortSrcName, shortDestName)
        copyCount += 1
        if (copyCount % 100) == 0:
            print("  Copied " + str(copyCount) + " files")



noCutoff_file.close()
mainLog_file.close()
print("\n\nDONE!\n")


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

