import re
from mishkal.tashkeel import TashkeelClass

vocalizer = TashkeelClass()

def egyptianize_text(text: str) -> str:
    # 1. Phonetic Swaps (The 'G' and 'A' sounds)
    # Note: This is subtle, we don't want to break the model, 
    # but we want to hint at the 'G' for Jeem.
    # For now, let's stick to the Vowels (Tashkeel) as it's safer.
    
    # 2. Add Tashkeel (The most important part for accent)
    vocalized_text = vocalizer.tashkeel(text)
    
    # 3. Manual Vowel Overrides for Egyptian "Melody"
    # Example: changing 'u' endings to 'o' sounds where appropriate
    return vocalized_text
