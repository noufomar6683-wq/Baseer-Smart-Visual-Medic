import cv2
import time
import pygame
import os
from roboflow import Roboflow

# --- 1. إعداد المسارات بدقة (لضمان الحفظ في مجلد test) ---
# المسار الحالي للمجلد (scripts)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# الانتقال للمجلد الرئيسي (Basser_Project)
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# تحديد مجلد الحفظ (test) ومجلد الأصوات (sounds)
TEST_DIR = os.path.join(BASE_DIR, "test")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

# إنشاء مجلد test تلقائياً إذا لم يكن موجوداً
if not os.path.exists(TEST_DIR):
    os.makedirs(TEST_DIR, exist_ok=True)

def get_sound_path(file_name):
    return os.path.join(SOUNDS_DIR, file_name)

# --- 2. إعداد النظام الصوتي ---
pygame.mixer.init()
sounds = {
    "start": pygame.mixer.Sound(get_sound_path("start.wav")),
    "welcome": pygame.mixer.Sound(get_sound_path("welcome.wav")),
    "heartbeat": pygame.mixer.Sound(get_sound_path("heartbeat.wav")),
    "b_alert": pygame.mixer.Sound(get_sound_path("b_alert.wav")),
    "b_steps": pygame.mixer.Sound(get_sound_path("b_steps.wav")),
    "f_alert": pygame.mixer.Sound(get_sound_path("f_alert.wav")),
    "f_steps": pygame.mixer.Sound(get_sound_path("f_steps.wav")),
    "critical": pygame.mixer.Sound(get_sound_path("critical.wav"))
}

# --- 3. تسلسل التشغيل (Start-up) ---
sounds["start"].play()
while pygame.mixer.get_busy(): continue 
sounds["welcome"].play()
while pygame.mixer.get_busy(): continue

# --- 4. تهيئة الذكاء الاصطناعي وكاميرا USB ---
API_KEY = "u0GLxXuomTNpsd3e4nrC"
rf = Roboflow(api_key=API_KEY)
project = rf.workspace().project("bleeding-fainting")
model = project.version(2).model

# استخدام الكاميرا رقم 1 (USB)
video = cv2.VideoCapture(1)

# --- 5. متغيرات التحكم ---
last_action_time = 0
last_detection_time = time.time()
last_save_time = time.time()
COOLDOWN_PERIOD = 30 

def silent_record(cap, duration, filename):
    """تسجيل فيديو في الخلفية وحفظه في مجلد test بصمت"""
    # استخدام ترميز MJPG لضمان التوافق والحفظ السريع
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    full_path = os.path.join(TEST_DIR, filename)
    out = cv2.VideoWriter(full_path, fourcc, 20.0, (640, 480))
    
    start_rec = time.time()
    while (time.time() - start_rec) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow("Basser Smart System", frame)
            cv2.waitKey(1)
        else:
            break
    out.release()

while True:
    ret, frame = video.read()
    if not ret: break
    current_time = time.time()

    # حفظ الصور (كل 5 ثوانٍ) بصمت داخل مجلد test
    if current_time - last_save_time > 5:
        img_name = f"cap_{time.strftime('%H%M%S')}.jpg"
        full_img_path = os.path.join(TEST_DIR, img_name)
        cv2.imwrite(full_img_path, frame)
        last_save_time = current_time

    # التحليل الذكي مع إدارة الأزمات
    if current_time - last_action_time > COOLDOWN_PERIOD:
        try:
            results = model.predict(frame, confidence=40).json()
            detected = [p['class'].lower() for p in results['predictions']]
            
            if detected:
                last_detection_time = current_time 
                case_name = ""
                
                if 'bleeding' in detected and 'fainting' in detected:
                    case_name = "Critical"
                    sounds["critical"].play() 
                    last_action_time = current_time 
                elif 'bleeding' in detected:
                    case_name = "Bleeding"
                    sounds["b_alert"].play() 
                    while pygame.mixer.get_busy(): pygame.time.Clock().tick(10)
                    time.sleep(2)
                    sounds["b_steps"].play()
                    last_action_time = current_time 
                elif 'fainting' in detected:
                    case_name = "Fainting"
                    sounds["f_alert"].play()
                    while pygame.mixer.get_busy(): pygame.time.Clock().tick(10)
                    time.sleep(2)
                    sounds["f_steps"].play()
                    last_action_time = current_time

                # تسجيل فيديو لمدة 15 ثانية فور الاستكشاف
                if case_name:
                    vid_name = f"{case_name}_{time.strftime('%H%M%S')}.avi"
                    silent_record(video, 20, vid_name)

            elif current_time - last_detection_time > 60:
                sounds["heartbeat"].play()
                last_detection_time = current_time
        except:
            pass 

    else:
        # إرشاد بصري بسيط على الشاشة
        cv2.putText(frame, "FOLLOW VOICE INSTRUCTIONS", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("Basser Smart System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

video.release()
cv2.destroyAllWindows()
