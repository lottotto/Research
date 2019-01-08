### 環境構築
```
pip install paho-mqtt pandas pyocr tensorflow opencv-python numpy
```
#### pyocrの構築
```
sudo apt-get install g++ # or clang++ (presumably)
sudo apt-get install autoconf automake libtool
sudo apt-get install autoconf-archive
sudo apt-get install pkg-config
sudo apt-get install libpng12-dev
sudo apt-get install libjpeg8-dev
sudo apt-get install libtiff5-dev
sudo apt-get install zlib1g-dev
wget http://www.leptonica.com/source/leptonica-1.74.4.tar.gz
tar xvzf leptonica-1.74.4.tar.gz
cd leptonica-1.74.4
./configure
make
sudo make install
git clone https://github.com/tesseract-ocr/tesseract.git
cd tesseract
./autogen.sh
./configure
make
sudo make install
```

[ここ](https://github.com/tesseract-ocr/tesseract/wiki/Data-Files)からeng.traineddataとjpn.traineddataをダウンロード  
/usr/local/share/配下におく
