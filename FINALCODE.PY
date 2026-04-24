import torch
import cv2
import numpy as np
import matplotlib.pyplot as plt
from torchvision import models, transforms
from PIL import Image
from IPython.display import display, Javascript
from base64 import b64decode


def capture_image(filename='captured.jpg'):
    js = Javascript('''
    async function takePhoto() {
      const div = document.createElement('div');
      const button = document.createElement('button');
      button.textContent = 'Capture';
      div.appendChild(button);

      const video = document.createElement('video');
      video.style.display = 'block';
      const stream = await navigator.mediaDevices.getUserMedia({video: true});

      document.body.appendChild(div);
      div.appendChild(video);
      video.srcObject = stream;
      await video.play();

      await new Promise((resolve) => button.onclick = resolve);

      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);

      stream.getTracks().forEach(track => track.stop());
      div.remove();

      return canvas.toDataURL('image/jpeg');
    }
    ''')
    display(js)
    try:
        data = eval_js('takePhoto()')
        binary = b64decode(data.split(',')[1])

        with open(filename, 'wb') as f:
            f.write(binary)

        return filename
    except Exception as e:
        print(f"Error capturing image: {e}. Please ensure camera permissions are granted and try again, or choose to upload an image.")
        return None


choice = input("1 = Upload, 2 = Capture: ")

if choice == '1':
    uploaded = files.upload()
    img_path = list(uploaded.keys())[0]
elif choice == '2':
    img_path = capture_image()
    if img_path is None:
        print("Image capture failed. Exiting to prevent further errors. Please re-run the cell and select '1' to upload an image.")
        exit() # Exit to prevent subsequent code from running with an invalid img_path
else:
    print("Invalid choice")
    exit()

image = Image.open(img_path).convert("RGB")
orig = np.array(image)

plt.imshow(orig)
plt.title("Original Image")
plt.axis('off')
plt.show()


hsv = cv2.cvtColor(orig, cv2.COLOR_RGB2HSV)

# Strict blue range
lower = np.array([90, 60, 50])
upper = np.array([140, 255, 255])

mask = cv2.inRange(hsv, lower, upper)

h, w = mask.shape


mask[0:int(0.3*h), :] = 0


kernel = np.ones((5,5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

mask = mask.astype(bool)


result = orig.copy()
result[mask] = [255, 0, 0]


plt.imshow(mask, cmap='gray')
plt.title("Water Mask (Sky Removed)")
plt.axis('off')
plt.show()

plt.imshow(result)
plt.title("Water Highlighted (FINAL FIXED)")
plt.axis('off')
plt.show()
