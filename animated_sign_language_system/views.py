from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
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
from .models import History, Favorite  # Importing History and Favorite models
from django.core.serializers.json import DjangoJSONEncoder  # For JSON encoding
from django.contrib import messages
from django import forms
from django.core.mail import send_mail
import random

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

            # NLP preprocessing
            text = contractions.fix(text)
            text = re.sub(r'[^\w\s]', ' ', text)  
            text = re.sub(r'\s+', ' ', text).strip()
            text = text.lower()

            words = word_tokenize(text)
            tagged = nltk.pos_tag(words)

            tense = {
                "future": len([word for word in tagged if word[1] == "MD"]),
                "present": len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]]),
                "past": len([word for word in tagged if word[1] in ["VBD", "VBN"]]),
                "present_continuous": len([word for word in tagged if word[1] == "VBG"]),
            }
            probable_tense = max(tense, key=tense.get)

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
                                
            # ✅ Check for missing animations
            missing_files = [w for w in processed_words if not finders.find(w + ".mp4")]
            if missing_files:
                print("Missing Animations:", missing_files)
                return render(request, 'animation.html', {'error': f"Missing animations for {', '.join(missing_files)}"})

            # ✅ Generate safe file names and paths
            # Replace spaces with underscores and remove special characters
            sanitized_text = text.replace(' ', '_')  # Turn spaces into underscores
            sanitized_text = re.sub(r'[^\w\-_]', '', sanitized_text)  # Clean any bad characters

            output_video_filename = f"{sanitized_text}.mp4"
            output_video_path = os.path.join(settings.MEDIA_ROOT, "animations", output_video_filename)
            os.makedirs(os.path.dirname(output_video_path), exist_ok=True)

            # ✅ Merge video clips using FFmpeg
            if video_clips:
                temp_list_file = os.path.join(settings.MEDIA_ROOT, "temp_list.txt")
                with open(temp_list_file, 'w') as file:
                    for clip in video_clips:
                        file.write(f"file '{clip}'\n")

                ffmpeg_cmd = [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", temp_list_file,
                    "-vf", "eq=brightness=0.2:contrast=1.4",
                    "-c:a", "copy",
                    output_video_path
                ]

                process = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print("FFmpeg Output:", process.stdout.decode())
                print("FFmpeg Error:", process.stderr.decode())

                if not os.path.exists(output_video_path):
                    return render(request, 'animation.html', {'error': "Animation merging failed!"})

            # ✅ Convert path to URL for frontend
            video_url = f"animations/{output_video_filename}"
            full_video_url = f"{settings.MEDIA_URL}{video_url}"

            # ✅ Save to History
            # ✅ Save to History only if not already present
            if not History.objects.filter(user=request.user, input_text=text).exists():
                History.objects.create(
                    user=request.user,
                    input_text=text,
                    keywords=json.dumps(filtered_words, cls=DjangoJSONEncoder),
                    video_path=video_url
                )

            # ✅ Store data in session for GET reload
            request.session['video_path'] = full_video_url
            request.session['entered_text'] = text
            request.session['filtered_keywords'] = filtered_words

            return redirect('animation')

        except Exception as e:
            print("Error:", e)
            return render(request, 'animation.html', {'error': "An unexpected error occurred."})

    # ✅ GET request: retrieve session values
    video_path = request.session.get('video_path', '')
    entered_text = request.session.get('entered_text', '')
    filtered_keywords = request.session.get('filtered_keywords', [])

    context = {
        'video_path': video_path,
        'entered_text': entered_text,
        'filtered_keywords': filtered_keywords
    }

    return render(request, 'animation.html', context)


@login_required(login_url="login")
def history_view(request):
    user_history = History.objects.filter(user=request.user).order_by('-created_at')
    favorite_video_paths = set(Favorite.objects.filter(user=request.user).values_list('video_path', flat=True))

    return render(request, 'history.html', {
        'history': user_history,
        'favorite_video_paths': favorite_video_paths,
    })

@login_required
def favorite_view(request):
    favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'favorites.html', {'favorites': favorites})

@login_required
def add_favorite(request, history_id):
    history_entry = get_object_or_404(History, id=history_id, user=request.user)
    if not Favorite.objects.filter(user=request.user, input_text=history_entry.input_text, video_path=history_entry.video_path).exists():
        Favorite.objects.create(
            user=request.user,
            input_text=history_entry.input_text,
            keywords=history_entry.keywords,
            video_path=history_entry.video_path
        )
    return redirect('favorite')

@login_required
def remove_favorite(request, favorite_id):
    favorite = get_object_or_404(Favorite, id=favorite_id, user=request.user)
    favorite.delete()
    return redirect('favorite')

@login_required(login_url="login")
def load_animation_from_history(request, video_filename):
    """Load animation from a specific video path from history/favorites."""
    video_path = f"animations/{video_filename}"
    full_video_url = f"{settings.MEDIA_URL}{video_path}"

    # Get text and keywords if possible (optional: enhance later)
    history_entry = History.objects.filter(user=request.user, video_path=video_path).first()
    entered_text = history_entry.input_text if history_entry else ''
    filtered_keywords = json.loads(history_entry.keywords) if history_entry else []

    context = {
        'video_path': full_video_url,
        'entered_text': entered_text,
        'filtered_keywords': filtered_keywords
    }

    return render(request, 'animation.html', context)

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

# Form for Forgot Password (email input)
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Enter your registered email")

# Form for entering OTP
class OTPVerificationForm(forms.Form):
    otp = forms.IntegerField(label="Enter the OTP sent to your email")

# Form for resetting password
class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(), label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

# View to request OTP
def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                otp = random.randint(100000, 999999)

                # Save OTP and email in session
                request.session['reset_email'] = email
                request.session['reset_otp'] = otp

                # Send OTP via email
                send_mail(
                    subject='Your OTP for Password Reset',
                    message=f'Your OTP for password reset is: {otp}',
                    from_email='nlpbasedanimationproject@gmail.com',  # use your Gmail here
                    recipient_list=[email],
                    fail_silently=False,
                )

                return redirect('verify_otp')
            except User.DoesNotExist:
                messages.error(request, "No user found with that email.")
    else:
        form = ForgotPasswordForm()

    return render(request, 'forgot_password.html', {'form': form})

# View to verify OTP
def verify_otp_view(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            saved_otp = request.session.get('reset_otp')

            if saved_otp and entered_otp == saved_otp:
                return redirect('reset_password')
            else:
                messages.error(request, "Invalid OTP.")
    else:
        form = OTPVerificationForm()

    return render(request, 'verify_otp.html', {'form': form})

# View to reset password
def reset_password_view(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_pass = form.cleaned_data['new_password']
            confirm_pass = form.cleaned_data['confirm_password']

            if new_pass != confirm_pass:
                messages.error(request, "Passwords do not match.")
            else:
                email = request.session.get('reset_email')
                try:
                    user = User.objects.get(email=email)
                    user.set_password(new_pass)
                    user.save()

                    # Clear session
                    request.session.pop('reset_email', None)
                    request.session.pop('reset_otp', None)

                    messages.success(request, "Password reset successful. You can now log in.")
                    return redirect('login')  # or your login view name
                except User.DoesNotExist:
                    messages.error(request, "Error resetting password.")
    else:
        form = ResetPasswordForm()

    return render(request, 'reset_password.html', {'form': form})


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