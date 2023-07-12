A module to anonymize Personal Identifiable Information (PII), utilizing the presidio package. The module operates as a service using fastAPI and currently supports Greek and English.

## PII anonymized:

The module can either hide PII or replace them with dummy values. Below are lists the detected entities and how they are handled respectively.

- Names: ANONYMOUS | Anonymous
- Location: HIDDEN_LOCATION | Generic Location
- Date & time: HIDDEN_DATE_TIME | HIDDEN Date or Time 
- Phone numbers: HIDDEN_PHONE_NUMBER | 123456
- Long numbers (e.g. Licenses, SSN): HIDDEN_LONG_NUMBER | 0000000000
- IBAN codes: HIDDEN_IBAN | Random two capital letters followed by 32 zeroes
- Credit card numbers: HIDDEN_CREDIT_CARD | 0000 0000 0000 0000
- E-mail address: HIDDEN_EMAIL | example@mail.com
- IP address: Masks last 6 digits | 127.0.0.1


## Modes

### Dummies mode (bool)
Choose whether to replace the anonymized values with dummy values or to simply hide them.

### Array mode (bool)
Opt to return an array in JSON format with the detected entities.

## Installation

- Install the required packages using the requirements.txt

- Install spaCy models for greek and english with:

    $ python -m spacy download el_core_news_lg
    
    $ python -m spacy download en_core_web_lg

- Start a local server using:

    $ python -m uvicorn main:pii_app --reload

- Connect to:

    localhost:8000/docs

- Use the 'Try it out' button and fill in the required parameters


## TODO

The module is, occasionally, unreliable at detecting names and locations in the greek language. Factors that affect this is spelling and use (or lack of use) of accents. Most often this is fixed with by restarting the service. It is, however, being worked on in order to improve performance.