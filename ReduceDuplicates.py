import os

imageExts = {'.jpg', '.cr2', '.gif'}
mainDict = {}

def CatalogFiles(path):
    dirContents = os.listdir(path)   # Get list of items in the current dir.
    for d in dirContents:
        newPath = os.path.join(path, d)
        if os.path.isdir(newPath):
            print("+  " + newPath)
            CatalogFiles(newPath)
        else:
            fileExt = os.path.splitext(d)
            if len(fileExt) == 2:
                if fileExt[1].lower() in imageExts:
                    print(" I " + newPath)
                    if d not in mainDict:
                        mainDict[d] = [newPath]
                    else:
                        mainDict[d].append(newPath)
                else:
                    print("   " + newPath)
            

CatalogFiles('Data')
print("\n")
for fileName, pathList in mainDict.items():
    print(fileName + "  " + str(len(pathList)))
    for path in pathList:
        print("   " + path)

# function doIt(path='.')
#   dirContents = os.listdir(path)
#   foreach entry in dirContents:
#     if (is directory(entry)):
#       doIt(entry)
#     else if (is Image File Extension):
#       dict[jpegFileName] += full path of entry  # list of paths that contain this file name

# function handleDuplicates(dict)
#   foreach k,v in dict:
#     if (length(v) == 1):                 # lone copy of file!
#       copy to dest dir with full path
#     else:
#       foreach path in v:
#         read jpeg exif data
#         os.stat(path)
#         if first, write down st_size, st_ctime/_atime/_mtime, based on what's right
#         if not first, compare st_size, times - close enough?  Wipe 
