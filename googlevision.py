import io
import cv2
from google.cloud import vision_v1p3beta1 as vision

# 이미지 파일 경로
image_path = r"C:\Users\fhrm0\Desktop\새 폴더\livre2.jpg"

# 이미지를 바이너리로 읽기
with io.open(image_path, 'rb') as image_file:
    content = image_file.read()

# Vision API에 이미지 바이너리 전송
client = vision.ImageAnnotatorClient()
image = vision.Image(content=content)

# 텍스트 출력 요청
response = client.text_detection(image=image)
texts = response.text_annotations

# 텍스트 출력
for text in texts:
    print(text.description)
