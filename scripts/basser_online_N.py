import cv2
from roboflow import Roboflow

# --- Your Credentials ---
API_KEY = "u0GLxXuomTNpsd3e4nrC"
MODEL_ID = "bleeding-fainting/2"

# Initializing Connection
rf = Roboflow(api_key=API_KEY)
project = rf.workspace().project("bleeding-fainting")
model = project.version(2).model


# 2. فتح كاميرا اللابتوب
video = cv2.VideoCapture(1)

print("جاري التشغيل... اضغط 'q' للخروج")

while True:
    ret, frame = video.read()
    if not ret:
        break

    # 3. إرسال الصورة للربوفلو والحصول على التوقعات (Inference)
    # ملاحظة: هذه العملية تعتمد على سرعة الإنترنت لأنها ترسل الصورة للسيرفر
    results = model.predict(frame, confidence=40, overlap=30).json()

    # 4. رسم المربعات على الشاشة
    for prediction in results['predictions']:
        x, y, w, h = int(prediction['x']), int(prediction['y']), int(prediction['width']), int(prediction['height'])
        label = prediction['class']
        # رسم المربع
        cv2.rectangle(frame, (int(x - w/2), int(y - h/2)), (int(x + w/2), int(y + h/2)), (0, 255, 0), 2)
        # كتابة اسم الكلاس (نزيف أو إغماء)
        cv2.putText(frame, label, (int(x - w/2), int(y - h/2) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Roboflow Live Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()