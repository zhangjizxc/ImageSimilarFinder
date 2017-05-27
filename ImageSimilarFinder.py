#!/usr/bin/env python
# coding=utf-8
import os
import PIL.Image
import shutil
import dhash
import datetime
# Allow library to be imported even if neither wand or PIL are installed
try:
    import wand.image
except ImportError:
    wand = None

try:
    import PIL.Image
except ImportError:
    PIL = None


targetDir= "/Users/zhangji/Downloads"
resultDir = targetDir + "/SimilarResults"
targetDirPathLen = len(targetDir)
imageSize = 8
limitDiff = 5


def load_image(filename):
    if wand is not None:
        return wand.image.Image(filename=filename)
    elif PIL is not None:
        return PIL.Image.open(filename)
    else:
        sys.stderr.write('You must have wand or Pillow/PIL installed to use the dhash command\n')
        sys.exit(1)


def findSimilarImgs(baseImageFile, tarDir, hasCmpedList, step):
    count = 0
    image1 = load_image(baseImageFile)
    hash1 = dhash.dhash_int(image1, size=imageSize)
    for path, d, filelist in os.walk(tarDir):
        if (not path.endswith('.git') and (not path.startswith(resultDir))):
            for filename in filelist:
                if (filename.endswith('jpg') or filename.endswith('png')):
                    count = count + 1
                    imageName = os.path.join(path, filename)

                    if (imageName not in hasCmpedList):
                        image2 = load_image(imageName)
                        hash2 = dhash.dhash_int(image2, size=imageSize)
                        num_bits_different = dhash.get_num_bits_different(hash1, hash2)
                        diff = 100 * num_bits_different/(imageSize * imageSize * 2)
                        if (diff <= limitDiff):
                            hasCmpedList.append(imageName)
                            print (baseImageFile +" is same with "+imageName)
                            movePicToResultDir(step, baseImageFile, imageName, diff)


def movePicToResultDir(hasCmpedLength, baseImageFile, similarImageFile, diff):
    moveToDir = resultDir+"/"+str(hasCmpedLength)
    if (not os.path.exists(moveToDir)):
        os.mkdir(moveToDir)
    filename1 = baseImageFile[targetDirPathLen+1:].replace('/', "_", 50)
    filenameWithPath1 = moveToDir + "/" + filename1
    if (not os.path.exists(filenameWithPath1)):
        shutil.copy(baseImageFile, filenameWithPath1)
    filename2 = similarImageFile[targetDirPathLen+1:].replace('/', "_", 50)
    filenameWithPath2 = moveToDir + "/" + str(diff) +"%_" + filename2
    shutil.copy(similarImageFile, filenameWithPath2)



if (os.path.exists(resultDir)):
    print('We need cLear the result dir')
    shutil.rmtree(resultDir, ignore_errors=False, onerror=None)

os.mkdir(resultDir)

hasCmpedList=[]
step=0
begin = datetime.datetime.now()
for path,d,filelist in os.walk(targetDir):
    if (not path.endswith('.git') and (not path.startswith(resultDir))):
        for filename in filelist:
            if (filename.endswith('jpg') or filename.endswith('png')):
                if (filename not in hasCmpedList):
                    step = step + 1
                    imageFileName = os.path.join(path, filename)
                    hasCmpedList.append(imageFileName)
                    findSimilarImgs(imageFileName, targetDir, hasCmpedList, step)

end = datetime.datetime.now()
print("Total Used Time: "+str(end-begin))
