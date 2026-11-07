import cv2
import time
import pygame
import os
from roboflow import Roboflow

# --- 1. إعداد المسارات (للوصول للمجلد الرئيسي ثم مجلد الأصوات) ---
# نستخدم os.path للوصول لمجلد sounds الموجود بجانب مجلد scripts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

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

# --- 3. تسلسل التشغيل الأولي ---
sounds["start"].play()
while pygame.mixer.get_busy(): continue 

sounds["welcome"].play()
while pygame.mixer.get_busy(): continue

# --- 4. تهيئة الذكاء الاصطناعي والكاميرا ---
# --- Your Credentials ---
API_KEY = "u0GLxXuomTNpsd3e4nrC"
MODEL_ID = "bleeding-fainting/2"

# Initializing Connection
rf = Roboflow(api_key=API_KEY)
project = rf.workspace().project("bleeding-fainting")
model = project.version(2).model
video = cv2.VideoCapture(1)

# --- 5. متغيرات التحكم وإدارة الوقت ---
last_action_time = 0
last_heartbeat_time = time.time() # توقيت بداية نبض النظام
COOLDOWN_PERIOD = 30 
current_status = "Monitoring..."

while True:
    ret, frame = video.read()
    if not ret: break
    current_time = time.time()

    # التحليل يعمل فقط خارج فترة "الهدوء الإسعافي"
    if current_time - last_action_time > COOLDOWN_PERIOD:
        current_status = "Active Monitoring"
        results = model.predict(frame, confidence=45).json()
        detected = [p['class'].lower() for p in results['predictions']]
        
        if detected:
            # حالة (1): نزيف وإغماء معاً (الملف الموحد)
            if 'bleeding' in detected and 'fainting' in detected:
                sounds["critical"].play() 
                last_action_time = time.time() 

            # حالة (2): نزيف فقط
            elif 'bleeding' in detected:
                sounds["b_alert"].play() 
                while pygame.mixer.get_busy(): pygame.time.Clock().tick(10)
                time.sleep(2) # وقفة سيكولوجية
                sounds["b_steps"].play()
                last_action_time = time.time() 

            # حالة (3): إغماء فقط
            elif 'fainting' in detected:
                sounds["f_alert"].play()
                while pygame.mixer.get_busy(): pygame.time.Clock().tick(10)
                time.sleep(2)
                sounds["f_steps"].play()
                last_action_time = time.time()
                
            # تصفير توقيت النبض عند رصد أي حالة لكي لا يشتغل النبض فوق صوت الإسعاف
            last_heartbeat_time = time.time()

        # --- إضافة تنبيه الـ 60 ثانية (Heartbeat) ---
        # يعمل فقط إذا لم يتم رصد أي حالة لمدة دقيقة كاملة
        elif current_time - last_heartbeat_time > 60:
            sounds["heartbeat"].set_volume(0.3) # صوت خفيف
            sounds["heartbeat"].play()
            last_heartbeat_time = current_time

    else:
        current_status = "AI Paused - Emergency Mode"
        cv2.putText(frame, "FOLLOW VOICE INSTRUCTIONS", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("Basser Smart System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

video.release()
cv2.destroyAllWindows()