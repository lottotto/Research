import New_Recoginizer
import ImageCut
import Keystone_correct
import CastResult_Publish
import re
import os
import sys


def main(srcPATH, StyleCsvPath):
    ret_correctedImagePaths = Keystone_correct.main(srcPATH)
    ret_ImageCut = []
    for path in ret_correctedImagePaths:
        ret_ImageCut.append(ImageCut.cutMain(PathToImage=path, PathToStyleCSV=StyleCsvPath))
    imagePathPattern = re.compile(r'images/.*\.jpg')
    for cutimages,SheatPATH in zip(ret_ImageCut, ret_correctedImagePaths):
        srcDirName = imagePathPattern.sub('texts',cutimages[0][0])
        os.mkdir(srcDirName)
        for i,(path, Recotype)in enumerate(cutimages):
            with open(os.path.join(srcDirName, str(i+1)+'.txt'),'w') as f:
                result =str(New_Recoginizer.Recognizer(path,Recotype))
                f.write(result)


if __name__ == '__main__':
    main(sys.argv[1], StyleCsvPath='./Resource/OCR_style20180919.csv')
