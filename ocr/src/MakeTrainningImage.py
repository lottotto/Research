import Keystone_correct
import ImageCut
import shutil
from datetime import datetime as dt

os.mkdir('./ConvertTemps')
corrected_Images = Keystone_correct.correct(srcPATH='./ConvertLearningImages', dstPATH='./ConvertTemps')
fileName = os.path.join('./TrainImageSet/',str(dt.now()))
os.mkdir(fileName)
for name in ['number', 'charactor', 'checkbox', 'other']:
    os.mkdir(os.path.join(fileName, name))

for images in corrected_Images:
    List = ImageCut.cutMain(PathToImage=images, PathToStyleCSV='./Resource/OCR_style20180715.csv')
    for l in List:
        pathList = l[0].split('/')
        name = pathList[-3]+'_'+pathList[-1]
        storeDir = os.path.join(fileName, l[1])
        tempImage = cv2.imread(l[0],0)
        cv2.imwrite(os.path.join(storeDir, name), tempImage)

shutil.rmtree('./ConvertTemps')
