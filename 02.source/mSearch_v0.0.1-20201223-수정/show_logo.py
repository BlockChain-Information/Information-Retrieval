import io
import os
import cv2
import pandas as pd
from datetime import datetime
import FinanceDataReader as fdr

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision_v1 import types


class Class_Logo:
    def __init__(self):
        self.clinent = None
        self.image = None
        self.response = None
        self.labels = None
        self.im = None

    def load_file(self, in_file_name):
        self.client = vision.ImageAnnotatorClient()
        with io.open(in_file_name, 'rb') as image_file:
            content = image_file.read()
        self.image = types.Image(content=content)
        self.im = cv2.imread(in_file_name)
        self.response = self.client.logo_detection(image=self.image)
        self.labels = self.response.logo_annotations

    def get_logo(self):
        out = []
        for label in self.labels:
            out.append(label.description)
        return out

    def set_img(self, out_file_name):
        for label in self.labels:
            box = [(vertex.x, vertex.y) for vertex in label.bounding_poly.vertices]
        #    price = self.get_stock_price(label.description)
            cv2.rectangle(self.im, box[0], box[2], (255, 0, 0), 1)
        #    cv2.putText(self.im, label.description + ":" + str(price), (box[0][0] + 10, box[0][1] + 20),
        #                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            cv2.putText(self.im, label.description , (box[0][0] + 10, box[0][1] + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

        cv2.imwrite(out_file_name, self.im)


        # cv2.imshow("logo", self.im)

    def get_stock_price(self, logo):
        code = self.get_code(logo)
        df_stock_price = fdr.DataReader(code, datetime.today(), datetime.today())
        out = df_stock_price['Close'][0]

        return out

    def get_code(self, name):
        df = pd.read_csv('stock.csv')
        code = df[df['Name'].str.contains(name, case=False)]['Symbol'].to_string(index=False)
        code = code.strip()
        print(code)
        return code

def main(args):

    lib_logo = Class_Logo()

    lib_logo.load_file(args)
    lib_logo.set_img('result1.jpg')

if __name__ == '__main__':
    main('nike.jpg')

