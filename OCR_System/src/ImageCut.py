import cv2
import csv
import os
import sys
import pandas as pd

def cutExcuse(PathToImage, x, y, frame_x, frame_y):
    srcImage = cv2.imread(PathToImage, cv2.IMREAD_GRAYSCALE)
    retImage = srcImage[y:y+frame_y, x:x+frame_x+1]
    return retImage

def cutMain(PathToImage, PathToStyleCSV):
    styleFile = open(PathToStyleCSV,'r',encoding='cp932')
    styleRows = csv.reader(styleFile)
    # styleRows = pd.read_csv(PathToStyleCSV, encoding='cp932')
    srcImageDirectoryName = os.path.dirname(PathToImage)
    StoreDirectoryName = os.path.join(srcImageDirectoryName, 'images')
    os.mkdir(StoreDirectoryName)
    count = 1
    storeFilePathList = []
    for row in styleRows:
        x = int(row[1])
        y = int(row[2])
        frames = int(row[3])
        frame_x = int(row[4])
        frame_y = int(row[5])
        character_type = row[6]
        for i in range(frames):
            cutImage = cutExcuse(PathToImage, x+i*frame_x, y, frame_x, frame_y)
            storeFilePathList.append((os.path.join(StoreDirectoryName, str(count)+'.jpg'), character_type))
            cv2.imwrite(storeFilePathList[-1][0], cutImage)
            count += 1

    return storeFilePathList

if __name__ == '__main__':
    cutMain(sys.argv[1], sys.argv[2])
