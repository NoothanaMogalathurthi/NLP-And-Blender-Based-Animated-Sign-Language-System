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

# Prerequisites
> -Python ≥ 3.7
> -Blender (For animation rendering)
> -NLTK Library (For text preprocessing)
> -WebkitSpeechRecognition API (For speech recognition)
> -SQLite  
> -Django (For backend processing)

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
8. Click on the microphone button to record speech input or manually enter text.
9. The system processes the input and displays the corresponding Indian Sign Language (ISL) animations in real time.
10. If a direct ISL animation is unavailable, the system will attempt to map synonyms or generate finger-spelling animations dynamically.