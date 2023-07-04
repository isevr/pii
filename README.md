A module to anonymize Personal Identifiable Information (PII), utilizing the presidio package.

## PII anonymized:
- Names
- Location
- Any numeric sequences
- E-mail address
- Political & Religious beliefs
- Blood type
- IP address

The module works for both the English and Greek languages. 


## Installation

Install spaCy models for greek and english with:

python -m spacy download el_core_news_lg
python -m spacy download en_core_web_lg