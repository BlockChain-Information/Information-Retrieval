# Information-Retrieval
정보검색


팀을 만들어 두었습니다

  https://github.com/orgs/BlockChain-Information/teams/information-retrieval  여기로 접속
  
  
# 주제 : Image Captioning


----
## Description
 
----
## Dataset
1. Flickr30k Dataset has been used for the training of model.
   [Flickr30K](https://www.kaggle.com/hsankesara/flickr-image-dataset)
2. Glove6B dataset [Link](https://drive.google.com/open?id=1GI5sWeCxgJEgToeVmakL69oDlXowXGU4)
----
## Reference Paper
* Paper:[Show and Tell: A Neural Image Caption Generator](https://arxiv.org/pdf/1411.4555.pdf)
* Paper:[Deep Visual-Semantic Alignments for Generating Image Descriptions](https://arxiv.org/pdf/1412.2306.pdf)
----
## Requirements
* Python
* Numpy

## Project Structure


## Model flow Chart
----
<img src="https://github.com/udaram/Image-Caption-Generator/blob/master/model.png">

    ```
## Run Model in steps
---
*Image Feature Extraction*
--------------------------
```
$ python3 ImageFeature_extraction.py
```
*Caption Preprocessing step*
--------------------------
```
$ python3 clean_captions.py
```
*Generating Vocabulary of Caption words*
--------------------------
```
$ python3 vocabulary.py
```
*Training of the Model*
--------------------------
```
$ python3 training.py
```
*Test model*
--------------------------
```
$ python3 gui.py

this gui is made using python Tkinter package 
```

## Testing The Model
---
model can be tested using below command after clonning the repository
```
$ python3 gui.py
```

*Test Results*
--------------
When you run the gui.py using above command it will show you welcome screen and will ask you to choose the image from your local directory. <br>
![alt text](https://github.com/udaram/Image-Caption-Generator/blob/master/TestResults/Screenshot%20from%202019-09-11%2014-38-26.png)
<br>
Here you can choose the Algorithm which you want to use to predict/generate a caption for chosen image.<br>
Here, some glimpses of Best results which i have got during testing.<br>
![alt text](https://github.com/udaram/Image-Caption-Generator/blob/master/TestResults/Screenshot%20from%202019-09-11%2013-24-39.png)
![alt text](https://github.com/udaram/Image-Caption-Generator/blob/master/TestResults/Screenshot%20from%202019-09-11%2013-20-31.png)
![alt text](https://github.com/udaram/Image-Caption-Generator/blob/master/TestResults/Screenshot%20from%202019-09-11%2013-23-04.png)
![alt text](https://github.com/udaram/Image-Caption-Generator/blob/master/TestResults/Screenshot%20from%202019-09-11%2013-19-46.png)
![alt text](https://github.com/udaram/Image-Caption-Generator/blob/master/TestResults/Screenshot%20from%202019-09-11%2013-25-17.png)
![alt text](https://github.com/udaram/Image-Caption-Generator/blob/master/TestResults/Screenshot%20from%202019-09-11%2014-12-09.png)
  
