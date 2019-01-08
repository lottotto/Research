import sys
from PIL import Image
import pyocr
import pyocr.builders


def other_Recognization(PathToImage):
    tools = pyocr.get_available_tools()
    tool = tools[0]
    txt = tool.image_to_string(
        Image.open(PathToImage),
        lang='jpn',
        builder=pyocr.builders.TextBuilder()
    )
#    print(txt)
    return txt

if __name__ == '__main__':
    other_Recognization(sys.argv[1])
