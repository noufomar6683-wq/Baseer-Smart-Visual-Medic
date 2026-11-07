import os

# 1. تحديد مسار مجلد المستندات (Documents) الخاص بالمستخدم الحالي آلياً
documents_path = os.path.join(os.path.expanduser('~'), 'Documents')

# 2. تحديد مسار مجلد المشاريع ومجلد مشروع بصير
projects_dir = os.path.join(documents_path, 'Projects')
basser_project_dir = os.path.join(projects_dir, 'Basser_Project')

# 3. قائمة المجلدات الفرعية المطلوب إنشاؤها داخل مشروع بصير
sub_folders = [
    'models',
    'scripts',
    'assets/sounds',
    'assets/images'
]

print(f"📂 جاري العمل في المسار: {projects_dir}")

# إنشاء المجلدات
try:
    # إنشاء مجلد Projects إذا لم يكن موجوداً
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)
        print(f"✅ تم إنشاء مجلد المشاريع الرئيسي: {projects_dir}")

    # إنشاء مجلد Basser_Project ومجلداته الفرعية
    for sub in sub_folders:
        path = os.path.join(basser_project_dir, sub)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"✅ تم إنشاء المجلد: {path}")
        else:
            print(f"⚠️ المجلد موجود مسبقاً: {path}")

    print(f"\n🎉 مبروك! الهيكل جاهز الآن في: \n{basser_project_dir}")

except Exception as e:
    print(f"❌ حدث خطأ أثناء إنشاء المجلدات: {e}")