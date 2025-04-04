from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import nltk
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required
import logging
import json
import os
import subprocess  # For FFmpeg animation merging
from django.conf import settings
import re
import contractions

logger = logging.getLogger(__name__)

def home_view(request):
    return render(request, 'home.html')

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

def load_custom_synonyms():
    """Loads custom synonym dictionary from a JSON file."""
    try:
        with open(settings.SYNONYM_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("Error: synonyms.json not found.")
        return {}
    except json.JSONDecodeError:
        logger.error("Error: Invalid JSON format in synonyms.json.")
        return {}

custom_synonyms = load_custom_synonyms()

def find_synonym(word):
    """Finds synonyms of a word using Custom Dictionary first, then WordNet."""
    if word in custom_synonyms:
        return custom_synonyms[word]

    synonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())

    return synonyms[0] if synonyms else None
@login_required(login_url="login")
def animation_view(request):
    if request.method == 'POST':
        try:
            text = request.POST.get('sen')

            if not text:
                return render(request, 'animation.html', {'error': "Please enter text."})
            print("Received Input:", text)

            text = contractions.fix(text)
            text = re.sub(r'[^\w\s]', ' ', text)  
            text = re.sub(r'\s+', ' ', text).strip()
            text = text.lower()

            words = word_tokenize(text)
            tagged = nltk.pos_tag(words)

            # Detect tense
            tense = {
                "future": len([word for word in tagged if word[1] == "MD"]),
                "present": len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]]),
                "past": len([word for word in tagged if word[1] in ["VBD", "VBN"]]),
                "present_continuous": len([word for word in tagged if word[1] == "VBG"]),
            }
            probable_tense = max(tense, key=tense.get)
            print(f"Chosen Tense: {probable_tense}")

            important_words = {"i", "he", "she", "they", "we", "what", "where", "how", "you", "your", "my", "name", "hear", "book", "sign", "me", "yes", "no", "not", "this", "it", "we", "us", "our", "that", "when"}
            stop_words = set(stopwords.words('english')) - important_words
            stop_words.update(['would', 'could', 'shall'])
            isl_replacements = {"i": "me"}
            lr = WordNetLemmatizer()

            filtered_words = []
            video_clips = []

            for word, tag in tagged:
                if word not in stop_words:
                    word = isl_replacements.get(word, word)
                    if tag in ['VBG', 'VBD', 'VBZ', 'VBN', 'NN']:
                        filtered_words.append(lr.lemmatize(word, pos='v'))
                    elif tag in ['JJ', 'JJR', 'JJS', 'RBR', 'RBS']:
                        filtered_words.append(lr.lemmatize(word, pos='a'))
                    else:
                        filtered_words.append(lr.lemmatize(word))

            #  Insert tense words AFTER filtering
            if probable_tense == "past" and tense["past"] > 0:
                filtered_words.insert(0, "Before")
            elif probable_tense == "future" and tense["future"] > 0:
                filtered_words.insert(0, "Will")
            elif probable_tense == "present_continuous" and tense["present_continuous"] > 0:
                filtered_words.insert(0, "Now")

            print(f"Final Processed Words: {filtered_words}")

            processed_words = []
            for w in filtered_words:
                path = w + ".mp4"
                animation_path = finders.find(path)

                if animation_path:
                    processed_words.append(w)
                    video_clips.append(animation_path)
                else:
                    synonym = find_synonym(w)
                    if synonym and finders.find(synonym + ".mp4"):
                        processed_words.append(synonym)
                        video_clips.append(finders.find(synonym + ".mp4"))
                    else:
                        for letter in w:
                            letter_path = letter + ".mp4"
                            if finders.find(letter_path):
                                video_clips.append(finders.find(letter_path))
                                processed_words.append(letter)

            missing_files = [w for w in processed_words if not finders.find(w + ".mp4")]
            if missing_files:
                print("Missing Animations:", missing_files)
                return render(request, 'animation.html', {'error': f"Missing animations for {', '.join(missing_files)}"})

            sanitized_text = re.sub(r'[^\w\-_]', '', text)
            output_video_filename = f"{sanitized_text}.mp4"
            output_video_path = os.path.join(settings.MEDIA_ROOT, "animations", output_video_filename)
            os.makedirs(os.path.dirname(output_video_path), exist_ok=True)

            if video_clips:
                temp_list_file = os.path.join(settings.MEDIA_ROOT, "temp_list.txt")
                with open(temp_list_file, 'w') as file:
                    for clip in video_clips:
                        file.write(f"file '{clip}'\n")

                ffmpeg_cmd = [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", temp_list_file, "-c", "copy", output_video_path
                ]

                process = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                print("FFmpeg Output:", process.stdout.decode())  # Debug
                print("FFmpeg Error:", process.stderr.decode())  # Debug
                
                if not os.path.exists(output_video_path):
                    return render(request, 'animation.html', {'error': "Animation merging failed!"})

            # Convert file path to a media URL
            video_url = f"{settings.MEDIA_URL}animations/{output_video_filename}"

            # ✅ **Store the text, extracted keywords & video in session**
            request.session['video_path'] = video_url
            request.session['entered_text'] = text
            request.session['filtered_keywords'] = filtered_words

            return redirect(request.path)

        except ValueError as ve:
            return render(request, 'animation.html', {'error': str(ve)})

        except Exception as e:
            return render(request, 'animation.html', {'error': "An unexpected error occurred."})

    # ✅ **Retrieve the stored values (if available)**
    video_url = request.session.get('video_path', '')
    entered_text = request.session.get('entered_text', '')
    filtered_keywords = request.session.get('filtered_keywords', [])
    # ✅ Debugging: Print values to check
    print("Session Video URL:", video_url)
    print("Session Entered Text:", entered_text)
    print("Session Filtered Keywords:", filtered_keywords)

    return render(request, 'animation.html', {
        'video_path': video_url,
        'entered_text': entered_text,
        'filtered_keywords': filtered_keywords
    })

# Signup view
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not email or not password1 or not password2:
            return render(request, 'signup.html', {'error': "All fields are required."})

        if password1 != password2:
            return render(request, 'signup.html', {'error': "Passwords do not match."})

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': "Email already exists."})

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            login(request, user)  
            return redirect('animation')
        except Exception as e:
            return render(request, 'signup.html', {'error': f"Error: {e}"})

    return render(request, 'signup.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')  
        password = request.POST.get('password')

        user = None

        if '@' in identifier:  
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                return render(request, 'login.html', {'error': "Invalid email or password."})
        else:
            user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            return redirect('animation')
        else:
            return render(request, 'login.html', {'error': "Invalid credentials."})

    return render(request, 'login.html')

# Logout view
def logout_view(request):
    try:
        logout(request)
        return redirect("home")
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return redirect("home")

# Custom 404 error page
def error_404_view(request, exception):
    return render(request, '404.html', status=404)

# Custom 500 error page
def error_500_view(request):
    return render(request, '500.html', status=500)

# Check if animation exists
def check_animation(request, word):
    """Checks if an animation file exists for the given word."""
    path = word + ".mp4"
    file_exists = bool(finders.find(path))
    return JsonResponse({'word': word, 'exists': file_exists})