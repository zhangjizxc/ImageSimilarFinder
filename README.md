# ImageSimilarFinder
这个工具是为了在Android源码中快速找出相似的图片，并进一步进行优化，减少编译生成的img的大小。

## 首先感谢开源项目dHash：https://github.com/Jetsetter/dhash
   
## 比较图片的原理：
1. 遍历指定文件中的所有图片，并按照长宽比进行归类。
2. 在已归类好的图片文件夹中，计算每一张图的dHash（mode=hex），根据算出来的值进行排序。
3. 计算dhash是按照指定的size，进行图片的缩放，然后对于缩放后的图的每一个像素点，进行两两比较，以0和1生成一个整型数值。
4. 对排序好的图片，进行相邻两张图的两两比较，计算diff.

## 用法：
```sh
ImageSimilarFinder.py  -s 16 -t 20 -p /Users/zhangji/Downloads/SimilarResults -f frameworks packages
```



