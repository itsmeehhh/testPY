import os
import random
import requests
from gtts import gTTS
from moviepy.editor import (
    ImageClip,
    concatenate_videoclips,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    vfx,
)

# اختيار صور عشوائية من مجلد الصور
image_folder = "./photos"
if not os.path.isdir(image_folder):
    raise Exception("Image folder does not exist.")

image_files = os.listdir(image_folder)
if not image_files:
    raise Exception("Image folder is empty.")

# اختيار 3 صور عشوائية
selected_images = random.sample(image_files, 4)

# تحويل النص إلى صوت باستخدام gTTS
api_url = "https://stoic-quotes.com/api/quotes"
response = requests.get(api_url)

if response.status_code == 200:
    quotes_data = response.json()

    if quotes_data:
        random_quote = random.choice(quotes_data)
        quote_text = random_quote.get("text", "لم يتم العثور على نص")

        tts = gTTS(text=quote_text, lang='en')
        audio_path = "quote_audio.mp3"
        tts.save(audio_path)

        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration

        # تقسيم النص إلى كلمات
        words = quote_text.split()
        word_clips = []

        # توزيع مدة الصوت على عدد الكلمات
        duration_per_word = audio_duration / len(words)

        # إنشاء مقاطع لظهور الكلمات بشكل تدريجي
        current_time = 0
        for word in words:
            word_clip = TextClip(
                txt=word,
                fontsize=30,  # تغيير حجم الخط
                color='white',
                font='Arial-Bold',
                size=(720, 1080),
            ).set_pos('center').set_duration(duration_per_word).set_start(current_time)  # وضع النص في وسط الصورة
            word_clips.append(word_clip)
            current_time += duration_per_word

        # إنشاء مقاطع فيديو من الصور مع تأثيرات الانتقال
        image_clips = []
        for img in selected_images:
            img_clip = ImageClip(os.path.join(image_folder, img))
            img_clip = img_clip.set_duration(current_time / len(selected_images))  # تعديل مدة الصورة
            img_clip = img_clip.crossfadein(0.5)
            image_clips.append(img_clip)

        # تجميع مقاطع الفيديو
        final_video = concatenate_videoclips(image_clips, method='compose')

        # دمج مقاطع الفيديو مع مقاطع الكلمات
        composite_clip = CompositeVideoClip([final_video] + word_clips)

        # دمج الصوت مع الفيديو
        composite_clip = composite_clip.set_audio(audio_clip)

        # حفظ الفيديو النهائي
        video_path = "output_video.mp4"
        composite_clip.write_videofile(video_path, fps=24)
        print("تم إنشاء الفيديو بنجاح:", video_path)

    else:
        print("لا توجد اقتباسات في البيانات المسترجعة.")
else:
    print("فشل في جلب الاقتباسات. كود الحالة:", response.status_code)
