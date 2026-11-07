import cv2
from ultralytics import YOLO
import pygame
import time
import os
from datetime import datetime

# --- 1. التأكد من وجود المجلدات قبل البدء (مهم جداً) ---
save_path = "../assets/images/"
if not os.path.exists(save_path):
    os.makedirs(save_path)
    print(f"📁 المجلد لم يكن موجوداً، تم إنشاء: {save_path}")

# --- 2. إعدادات الصوت والموديل ---
pygame.mixer.init()
sound_file = "../assets/sounds/person.mp3"
model = YOLO('../models/baseer_model_v1.pt')

cap = cv2.VideoCapture(1) 

# --- 3. متغيرات التحكم ---
BOOT_IMAGE_COUNT = 10    
boot_image_counter = 0    
IS_BOOTING = True        
last_save_time = 0
last_speech_time = 0

print("🟢 النظام بدأ.. جاري التقاط 10 صور توثيقية أولية...")

while True:
    ret, frame = cap.read()
    if not ret: break

    current_time = time.time()

    if IS_BOOTING:
        # مرحلة التقاط الصور الـ 10 الأولى
        if (current_time - last_save_time > 0.5):
            if boot_image_counter < BOOT_IMAGE_COUNT:
                timestamp = datetime.now().strftime('%H%M%S_%f')
                # الحفظ الآن آمن لأننا تأكدنا من المجلد في الأعلى
                img_name = f"BOOT_{boot_image_counter + 1}_{timestamp}.jpg"
                cv2.imwrite(os.path.join(save_path, img_name), frame)
                
                print(f"📸 حفظ صورة توثيقية: {img_name}")
                last_save_time = current_time
                boot_image_counter += 1
            else:
                IS_BOOTING = False
                print("✅ انتهى التوثيق الأولي. وضع المراقبة الذكي يعمل الآن...")
        
        cv2.imshow("Basser AI - Booting...", frame)

    else:
        # وضع المراقبة (YOLO)
        results = model(frame, stream=True, verbose=False, conf=0.5)
        emergency_detected = False
        annotated_frame = frame.copy()

        for r in results:
            if len(r.boxes) > 0:
                emergency_detected = True
                annotated_frame = r.plot()

        if emergency_detected and (current_time - last_speech_time > 5):
            if os.path.exists(sound_file):
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                last_speech_time = current_time

        cv2.imshow("Basser AI - Monitoring Mode", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()