A module to anonymize Personal Identifiable Information (PII), utilizing the presidio package. The module operates as a service using fastAPI and currently supports Greek and English.

## PII anonymized:
- Names (Currently sometimes unreliable in greek version)
- Location
- Date and time (Currently sometimes unreliable in greek version)
- Phone numbers
- Long numbers (e.g. Licenses, SSN)
- IBAN codes
- Credit card numbers
- E-mail address
- IP address


## Modes

### Dummies mode (bool)
Choose whether to replace the anonymized values with dummy values or to simply hide them.

### Array mode (bool)
Opt to return an array in JSON format with the detected entities.

## Installation

- Install the required packages using the requirements.txt

- Install spaCy models for greek and english with:

    python -m spacy download el_core_news_lg
    python -m spacy download en_core_web_lg

- Start a local server using:

    $ python -m uvicorn main:pii_app --reload

- Connect to:

    localhost:8000/docs

- Use the 'Try it out' button and fill in the required parameters