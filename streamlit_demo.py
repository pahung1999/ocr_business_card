import streamlit as st
import os
import time
from ocr import *
import requests


os.system("clear")
st.set_page_config(layout="wide")

api_url="http://10.10.1.37:10000/ocr/"
st.header("OCR Business Card")

upload_methods = ["Từ thư viện trong máy"] #, "Chụp ảnh mới"]
upload_method = st.radio("Phương pháp upload ảnh", upload_methods)

image_file = st.file_uploader("Upload file")

left, right = st.columns(2)

if image_file is not None:
    #images= convert_from_bytes(image_file.getvalue())
    left.image(image_file,use_column_width="always")
    nparr = np.fromstring(image_file.getvalue(), np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    submit = left.button("Nhận dạng")
else:
    submit = clear = False



if submit:
    with st.spinner(text="Processing..."):
        a=time.time()
        post_param = dict(box_format = "xyxy",remove_anomalies=True,output_features='fulltext')
        res = requests.post(api_url, files=dict(image=image_file.getvalue()), data=post_param)
        
        b=time.time()
        texts,boxes,fulltext=res.json()['results'][0]['texts'],res.json()['results'][0]['boxes'],res.json()['results'][0]['fulltext']
        # merged_boxes=[convert_xyxy_poly(box) for box in boxes]
        merged_boxes=boxes
        # fulltext=fulltext.replace("\n","|")
        merged_texts=fulltext.split("\n")
        
        #In ảnh vẽ bouding box
        for box in merged_boxes:
            img_np=bounding_box(box[0],box[1],box[2],box[3],img_np)
        right.image(img_np)

        #Gộp text và ngắt dòng:
        bboxes=[]
        raw_texts=[]
        for i in range(len(texts)):
            bboxes.insert(0, boxes[i])
            raw_texts.insert(0, texts[i])
        h,w,c=img_np.shape
        g = arrange_bbox(bboxes)
        rows = arrange_row(g=g)
        rows=split_row(rows,bboxes,ratio=0.5)
        for i in range(len(rows)):
            text_row=""
            for j in rows[i]:
                text_row+=" "+raw_texts[j]
            right.write(text_row.strip())

        # In kết quả đã gộp
        # for text in merged_texts:
        #     right.write(text)


        # right.write(fulltext)
        right.write(f"Thời gian đọc là: {b-a}s")