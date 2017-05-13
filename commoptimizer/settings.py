import os


def get_cta_api_key():
    cta_api_key = os.getenv('CTA_API_KEY')
    if not cta_api_key:
        raise ValueError('No CTA API key found! Please set environment variable $CTA_API_KEY')

    return cta_api_key
