import os
from django.conf import settings

def load_spam_words():
    with open(os.path.join(settings.BASE_DIR, 'spam_words.txt'), 'r') as file:
        return [word.strip().lower() for word in file.read().split(',')]