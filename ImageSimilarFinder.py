#!/usr/bin/env python
# coding=utf-8
import os
import shutil
import dhash
import datetime
import PIL
import sys
# Allow library to be imported even if neither wand or PIL are installed
try:
    import wand.image
except ImportError:
    wand = None

try:
    from PIL import Image
except ImportError:
    PIL = None


def load_image(filename):
    image = None
    if wand is not None:
        try:
          image=wand.image.Image(filename=filename)
        except:
          image = None
        return image
    elif PIL is not None:
        try:
          image=PIL.Image.open(filename)
        except:
          image = None
          print(filename+" is not a invalid img!")
        return image
    else:
        sys.stderr.write('You must have wand or Pillow/PIL installed to use the dhash command\n')
        sys.exit(1)


def findSimilarImgs(baseImageFile, tarDir, hasCmpedList, step):
    count = 0
    image1 = load_image(baseImageFile)
    if image1 is None:
        return
    try:
        hash1 = dhash.dhash_int(image1, size=imageSize)
    except:
      return
    for path, d, filelist in os.walk(tarDir):
        if (not path.endswith('.git') and (not path.startswith(resultDir))):
            for filename in filelist:
                if (filename.endswith('jpg') or filename.endswith('png')):
                    count = count + 1
                    imageName = os.path.join(path, filename)
                    if (imageName not in hasCmpedList):
                        image2 = load_image(imageName)
                        if image2 is not None:
                            try:
                             hash2 = dhash.dhash_int(image2, size=imageSize)
                            except:
                              continue
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

def isPathInList(list, path):
    if (len(list) == 1 and list[0] == 'ALL'):
        return True
    for item in list:
        if (path is not None and path.startswith(item)):
            return True
    return False

def arrangePics(targetDir, picDir):
    targetDirPathLen=len(targetDir)
    count=0
    for path, d, filelist in os.walk(targetDir):
        if (not path.endswith('.git')) and isPathInList(targetLimitedSubDirs, path):
            for filename in filelist:
                if (filename.endswith('jpg') or filename.endswith('png') or filename.endswith('jpeg') or filename.endswith('gif')):
                    fileNameWithPath = os.path.join(path, filename)
                    image = load_image(fileNameWithPath)
                    if (image is not None):
                        ratio = format(float(image.height) / float(image.width), '.2f')
                        tempPath = os.path.join(picDir, str(ratio))
                        if (not os.path.exists(tempPath)):
                            os.mkdir(tempPath)
                        filenameNew=fileNameWithPath[targetDirPathLen+1:].replace('/', "_", 50)
                        tempFileNameWithPath = os.path.join(tempPath, filenameNew)
                        print(fileNameWithPath+"  copy to "+tempFileNameWithPath)
                        count = count + 1
                        shutil.copy(fileNameWithPath, tempFileNameWithPath)
    print("Total Image count is "+str(count))

def sortPicsBySimilarity(allPicsDir, imageSize, threshold, sortedPicsDir, similarPicsDir):
       allPicsDirLen = len(allPicsDir) 
       for path,d,filelist in os.walk(allPicsDir):
        L = []
        for filename in filelist:
            fileNameWithPath = os.path.join(path, filename)
            image = load_image(fileNameWithPath)
            if image is not None:
                try:
                    hash = dhash.dhash_int(image, size=imageSize)
                except:
                    continue
            L.append((hash, filename))

        sortedPath = os.path.join(sortedPicsDir, path[allPicsDirLen+1:])
        similarPath = os.path.join(similarPicsDir, path[allPicsDirLen+1:])
        if not os.path.exists(sortedPath):
            os.mkdir(sortedPath)
        if not os.path.exists(similarPath):
            os.mkdir(similarPath)
        S = sorted(L, key=lambda l: l[0])
        count = 0
        for item in S:
            origFile = os.path.join(path, item[1])
            if count > 0:
                lastItem = S[count-1]
                hash1 = lastItem[0]
                hash2 = item[0]
                num_bits_different = dhash.get_num_bits_different(hash1, hash2)
                diff = 100 * num_bits_different / (imageSize * imageSize * 2)
                newFileName = str(count) + "_" + str(diff) + "%_" + item[1]
                if diff <= threshold:
                   shutil.copy(origFile, os.path.join(similarPath, newFileName))
                   if count == 1:
                       lastNewFileName = str(count - 1)+"_"+lastItem[1]
                   else:
                       lastNewFileName = str(count - 1)+ "_" + str(lastDiff) + "%_" + lastItem[1]
                   lastNewFilePath=os.path.join(similarPath, lastNewFileName)
                   if not os.path.exists(lastNewFilePath):
                      shutil.copy(os.path.join(path, lastItem[1]), lastNewFilePath)
                lastDiff=diff
            else:
                newFileName = str(count)+"_"+item[1]
            shutil.copy(origFile, os.path.join(sortedPath, newFileName))
            count = count+1

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--size', type=int, default=16,
                        help='width and height of dhash image size, default %(default)d')
    parser.add_argument('-t', '--threshold', type=int, default=20,
                        help='The threshold to judge whether similar image or not')
    parser.add_argument('-p', '--path', nargs='?',
                        help='The path to find.')
    parser.add_argument('-f', '--filter', nargs='*',
                        help='The sub dirs to compare together.')
    args = parser.parse_args()

    if (args.path is None):
        sys.stderr.write('You must specified path.Use -h for help.\n')
        sys.exit(1)

    targetDir = args.path
    targetLimitedSubDirs=[]
    if args.filter is None:
        targetLimitedSubDirs.append("ALL")
    else:
        for subdir in args.filter:
            targetLimitedSubDirs.append(os.path.join(targetDir,subdir))
    print targetLimitedSubDirs
    resultDir = targetDir + "/../SimilarImgResults"
    allPicsDir = resultDir + "/AllPics"
    sortedPicsDir = resultDir+"/SortedPics"
    similarPicsDir = resultDir+"/SimilarPics"
    imageSize = args.size
    threshold = args.threshold

    begin = datetime.datetime.now()

    if (os.path.exists(resultDir)):
        print('We need cLear the result dir')
        shutil.rmtree(resultDir, ignore_errors=False, onerror=None)
    os.mkdir(resultDir)
    os.mkdir(allPicsDir)
    os.mkdir(sortedPicsDir)
    os.mkdir(similarPicsDir)

    arrangePics(targetDir, allPicsDir)
    sortPicsBySimilarity(allPicsDir,imageSize, threshold, sortedPicsDir, similarPicsDir)
    
    end = datetime.datetime.now()
    print("Finished! Total Used Time: " + str(end - begin)+"  Pls check the dir "+resultDir)
