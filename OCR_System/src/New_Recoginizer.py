import image_predict
import Checkbox_reco
import Other_reco
import cv2
import numpy as np

def detect_space(PathToImage):
    Image = cv2.imread(PathToImage,cv2.IMREAD_GRAYSCALE)
    Image = Image[7:23, 7:23]
    temp_Image = cv2.threshold(Image,135,255,cv2.THRESH_BINARY)[1]
    if np.count_nonzero(temp_Image)/temp_Image.size > 0.98:
        return True
    else:
        return False

def Recognizer(PathToImage, RecoType):
    if RecoType == 'other':
        return "Need PyOCR"
        # return Other_reco.other_Recognization(PathToImage)
    elif RecoType == 'checkbox':
        return Checkbox_reco.main(PathToImage)
    else:
        if detect_space(PathToImage):
            return '-'
        else:
            return image_predict.main(PathToImage, RecoType)

if __name__ == '__main__':
    Recognizer(sys.argv[1], sys.argv[2])
