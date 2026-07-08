#
#   test_gemini_key.py
#
#   Minimal check that a Gemini API key works. Makes one tiny generate call and
#   reports success or the exact error.
#
#   Usage (PowerShell):
#     $env:GEMINI_API_KEY="..."; python test_gemini_key.py
#   or pass the key / model as arguments (key is visible in shell history this way):
#     python test_gemini_key.py <API_KEY> [model]
#
#   Default model is gemini-2.5-flash (fast/cheap for a key check). Pass
#   gemini-2.5-pro as the 2nd argument to test the model the module uses by default.

import os
import sys


def main():
    # Key: 1st arg, else env var.
    key = None
    if len(sys.argv) > 1 and sys.argv[1].strip():
        key = sys.argv[1].strip()
    else:
        key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')

    model = sys.argv[2].strip() if len(sys.argv) > 2 else 'gemini-2.5-flash'

    if not key:
        print('No key found. Set GEMINI_API_KEY (or GOOGLE_API_KEY), or pass the key as the first argument.')
        return

    print('Key length: %d, starts with: %s...' % (len(key), key[:6]))
    print('Testing model: %s' % model)

    try:
        from google import genai

    except ImportError:
        print('The google-genai package is not installed in this Python. Install it with:')
        print('    python -m pip install google-genai')
        return

    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=model,
            contents='Reply with exactly the two characters: OK',
        )
        text = (getattr(response, 'text', None) or '').strip()
        print('\nSUCCESS - the key works.')
        print('Model replied: %r' % text)

    except Exception as err:
        print('\nFAILED - the key did not work (or the model is not available to it).')
        print('%s: %s' % (type(err).__name__, err))
        print('\nCommon causes: wrong/expired key, the key\'s project has the Generative Language API disabled,')
        print('billing/quota, or the model name is not available to your key. Get or check a key at')
        print('https://aistudio.google.com/apikey')


if __name__ == '__main__':
    main()
