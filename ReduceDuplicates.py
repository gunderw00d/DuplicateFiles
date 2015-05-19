import os
import functools
import shutil
import win32api

imageExts = {'.jpg', '.jpeg', '.cr2', '.nef', '.gif', '.tif', '.tiff', '.png', '.bmp', '.psd', '.ppm'}
mainDict = {}
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


fnameSizeDict = {}

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


copyCommands = []
mkdirsCommands = []

def GenerateCommands():
    uniqueFileBase='Unique'
    print("\n")
    for fileName, pathList in mainDict.items():
        print(fileName)
        # generate a set of "copy <path> <newPath>" commands
        newCopies = {}
        for path in pathList:
            print("    " + path)
            pathComponents = path.split('\\')
            #print(pathComponents)
            subPath = functools.reduce(os.path.join, pathComponents[2:])
            #print("    " + subPath)
            if subPath not in newCopies.keys():
                targetLoc = os.path.join(uniqueFileBase, subPath)
                newCopies[subPath] = [path, targetLoc]
            #else - check file size - same? skip, different? change file name and copy
        copyCommands.extend(newCopies.values())

    # generate a set of mkdir commands off the copy commnads
    fooBar = {}
    for cpCmd in copyCommands:
        prefix, filename = os.path.split(cpCmd[1])
        #print(cpCmd[1])
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
    
            

# find all files
# build copy commands list:
#   find common paths
#   if file path & size the same, copy to target dir
#   if path same but size differ - copy to target dir, change names.
#   if paths differ - copy to different target dirs separately.
#   LOG EVERYTHING
#pathBase = 'Data\\'
#pathBase="C:\\Users\\Greg\\Documents\\Projects\\DuplicateFiles\\Data"
pathBase=["E:\\2TB_Drive", "E:\\2TB_JanBackup", "E:\\4TB_Backup", "E:\\C_Drive", "E:\\Seagate Dashboard 2.0"]

for path in pathBase:
    CatalogFiles(win32api.GetShortPathName(path))


count = 0
for k in mainDict.keys():
    count += len(mainDict[k])
#print("  " + str(sum))

print(str(len(mainDict.keys())) + " files in " + str(count) + " paths")

ReSortBySize()

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

#extens = []
#extens.extend(extensions.keys())
#extens.sort()
#for ext in extens:
#    print(ext)

