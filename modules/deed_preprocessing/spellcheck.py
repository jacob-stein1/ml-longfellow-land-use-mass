from autocorrect import Speller

# Initialize the Speller instance from autocorrect
spell = Speller(lang='en')

def correct_spelling(text):
    """Correct spelling using Autocorrect."""
    
    # Correct basic spelling errors using Autocorrect
    corrected_text = spell(text)
    
    return corrected_text
