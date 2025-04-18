# Animated-Sign-Language-System
# NLP and Blender Based Animated Indian Sign Language System
A web application that converts spoken or typed text into Indian Sign Language (ISL) animations using Natural Language Processing (NLP) and 3D animations in Blender.

# Overview
This project aims to bridge the communication gap for the deaf and hard-of-hearing community by converting text into animated sign language gestures. It processes input using NLP techniques and displays 3D animated ISL signs in real-time.

# Features
> -Speech-to-Text Conversion: Uses WebkitSpeechRecognition API for real-time voice input processing.
> -Text Processing & NLP: Implements Natural Language Toolkit (NLTK) for text segmentation, synonym mapping, and preprocessing to match ISL grammar.
> -Sign Language Animation: Uses Blender to generate 3D character animations for ISL signs.
> -Synonym Recognition: Maps words to their ISL equivalents for better coverage of vocabulary.
> -User-Friendly Interface: Web-based front-end built with HTML, CSS, and JavaScript.
> -If a direct ISL sign video is missing: Check for a synonym and even if the synonym is missing then it Fall back to fingerspelling(letter-by-letter animation)
> -ISL Animation Generation via FFmpeg: Merges multiple sign animations into one seamless video using FFmpeg.
> -Live Word Highlighting: Dynamically highlights each sign/word being animated during playback using JavaScript syncing.
> -History Tracking: Saves every animation generated, along with its keywords and timestamp.
> -Favorites System: Lets users mark frequently used inputs as favorites.

# Prerequisites
> -Python ≥ 3.7
> -Blender (For animation rendering)
> -NLTK Library (For text preprocessing)
> -WebkitSpeechRecognition API (For speech recognition)
> -SQLite  
> -Django (For backend processing)
> -FFmpeg (Must be installed and added to PATH)

# Installation Guide
These instructions will help you download, set up, and run the project on your local machine for development and testing purposes.

# Instructions
1. Download or clone the project repository to your local system.
2. Open the project folder and launch the terminal or command prompt.
3. Ensure all required dependencies are installed as mentioned in the Prerequisites section.
4. Run the Python file using the command "python manage.py runserver" to start the Django development server.
5. The terminal will display a localhost address (e.g., "server at http://127.0.0.1:8000/").
6. Open a web browser and enter the localhost address to access the application.
7. Sign up or log in to start using the system.
8. If you forget your password, click on “Forgot Password?” on the login page and follow the steps to reset it using OTP-based verification.
9. Click on the microphone button to record speech input or manually enter text.
10. The system processes the input and displays the corresponding Indian Sign Language (ISL) animations in real time.
11. If a direct ISL animation is unavailable, the system will attempt to map synonyms or generate finger-spelling animations dynamically.
12. The animation video will play on the screen, and the respective signs (words/letters) will be highlighted beside the video as they are played in the keywords list.
13. Every generated animation video includes a download button so users can save the video locally.
14. Every generated animation video includes a playback speed control option so users can adjust the video speed.
15. After each animation is generated, it will be automatically saved to the History page under your user account.
16. Visit the History page to view all previously generated animations. Each entry includes the input text, ISL keywords, timestamp, and a clickable animation filename link.
17. From the History page, you can click the “Add to Favorite” button to mark specific animations as favorites.
18. Visit the Favorites page to view and manage your saved animations. These are also listed with clickable links that redirect to the animation page.
 

