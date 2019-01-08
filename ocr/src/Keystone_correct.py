import cv2
import numpy as np
import os
import re
from datetime import datetime
import sys

A4WIDTH_MM = 210
DocSize = (182, 269)
template = cv2.imread('./Resource/60_marker.png',0)
#template = cv2.imread('./Resource/100_marker.jpg',0) #style_csv作るときはこっち
marker_shape = template.shape[::-1]

def resize(Image):
    resized_img = cv2.resize(Image,(737, 1089))
    return resized_img

def detect_marker(Image):
    img_gray = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    markerposarray = []
    for i in range(4):
        (minval, maxval, minloc, maxloc) = cv2.minMaxLoc(res)
        a = maxloc[0] + int(marker_shape[0]/2)
        b = maxloc[1] + int(marker_shape[1]/2)
        markerposarray.append(tuple([a,b]))
        cv2.circle(res, maxloc,30, (0.0), -1)
    return markerposarray

def sort_center_point(List):
    sumList = []
    temp = []
    result = []
    for i in range(4):
        sumList.append(sum(List[i]))
    sumList.sort()
    for sl in sumList:
        for l in List:
            if sum(l) == sl:
                temp.append(l)
    result.append(temp[0])
    result.append(temp[1])
    result.append(temp[3])
    result.append(temp[2])
    return result


def transform(image, points, dpmm):
    docpxls = (int(DocSize[0] * dpmm),int(DocSize[1]*dpmm))
    docrect = np.array([(0,0), (docpxls[0], 0), (docpxls[0], docpxls[1]), (0, docpxls[1])],'float32')
    transmat = cv2.getPerspectiveTransform(np.array(points, 'float32'), docrect)
    return cv2.warpPerspective(image, transmat, docpxls)

def correctKeyStone(image):
    center_point_list = detect_marker(image)
    center_point_list = sort_center_point(center_point_list)
    dpmm = min(image.shape[0:2]) / A4WIDTH_MM
    dst = transform(image, center_point_list, dpmm)
    dst = resize(dst)
    return dst

def main(srcPATH):
    retList = []#補正後画像へのパスの集合
    file = os.path.split(srcPATH)[0]
    storedDirectoryName = file
    image = cv2.imread(srcPATH)

    #例外処理　マーカーが認識できなかった時
    try:
        image = correctKeyStone(image)
        retList.append(os.path.join(storedDirectoryName, 'corrected.jpg'))
    except:
        print("{}, {}, Can not detect marker.".format(datetime.now().strftime("%Y%m%d-%H%M%S"), srcPATH))
        retList.append(os.path.join(storedDirectoryName, 'MarkerDetect_Error.jpg'))
        return []

    #例外処理 imageがimageじゃなかったとき
    try:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except:
        print("{}, {}, Maybe It is not Image File.".format(datetime.now().strftime("%Y%m%d-%H%M%S"), srcPATH))
        return []
    # ret1,th1 = cv2.threshold(image,0,255,cv2.THRESH_OTSU)
    cv2.imwrite(retList[-1], image)
    return retList

if __name__ == '__main__':

    """
        使い方
        python Keystone_correct.py hogehoge
        hogehoge: 変換したい画像が入っているフォルダ
        戻り値
        変換された画像をプログラム起動時間をフォルダ名としたファイルに入れます．

    """
    main(sys.argv[1])
