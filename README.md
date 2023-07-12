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


## Example Outputs

### Anonymized text for input in Greek

Input:
```
Με λένε Ελένη. Το IP μου ειναι 192.168.0.1 και η πιστωτική μου κάρτα είναι 1234 1234 1234 1234
```

Output:
```
"Με λένε ANONYMOUS. Το IP μου ειναι 192.16***** και η πιστωτική μου κάρτα είναι HIDDEN_CREDIT_CARD."
```
### Full JSON Output for input in English

Input:
```
Hello, my name is John. I live in London and i am 25 years old. My email address is thismail@gmail.com
```

Output:
```
{
  "Anonymized text": "Hello, my name is ANONYMOUS. I live in HIDDEN_LOCATION and i am HIDDEN_DATE_TIME. My email address is HIDDEN_EMAIL.",
  "Entity Array": [
    {
      "entity_type": "EMAIL_ADDRESS",
      "start": 84,
      "end": 102,
      "score": 1,
      "analysis_explanation": {
        "recognizer": "EmailRecognizer",
        "pattern_name": "Email (Medium)",
        "pattern": "\\b((([!#$%&'*+\\-/=?^_`{|}~\\w])|([!#$%&'*+\\-/=?^_`{|}~\\w][!#$%&'*+\\-/=?^_`{|}~\\.\\w]{0,}[!#$%&'*+\\-/=?^_`{|}~\\w]))[@]\\w+([-.]\\w+)*\\.\\w+([-.]\\w+)*)\\b",
        "original_score": 0.5,
        "score": 1,
        "textual_explanation": null,
        "score_context_improvement": 0.5,
        "supportive_context_word": "email",
        "validation_result": true
      },
      "recognition_metadata": {
        "recognizer_name": "EmailRecognizer",
        "recognizer_identifier": "EmailRecognizer_2348946225808"
      }
    },
    {
      "entity_type": "PERSON",
      "start": 18,
      "end": 22,
      "score": 0.85,
      "analysis_explanation": {
        "recognizer": "SpacyRecognizer",
        "pattern_name": null,
        "pattern": null,
        "original_score": 0.85,
        "score": 0.85,
        "textual_explanation": "Identified as PERSON by Spacy's Named Entity Recognition",
        "score_context_improvement": 0,
        "supportive_context_word": "",
        "validation_result": null
      },
      "recognition_metadata": {
        "recognizer_name": "SpacyRecognizer",
        "recognizer_identifier": "SpacyRecognizer_2348682647184"
      }
    },
    {
      "entity_type": "LOCATION",
      "start": 34,
      "end": 40,
      "score": 0.85,
      "analysis_explanation": {
        "recognizer": "SpacyRecognizer",
        "pattern_name": null,
        "pattern": null,
        "original_score": 0.85,
        "score": 0.85,
        "textual_explanation": "Identified as GPE by Spacy's Named Entity Recognition",
        "score_context_improvement": 0,
        "supportive_context_word": "",
        "validation_result": null
      },
      "recognition_metadata": {
        "recognizer_name": "SpacyRecognizer",
        "recognizer_identifier": "SpacyRecognizer_2348682647184"
      }
    },
    {
      "entity_type": "DATE_TIME",
      "start": 50,
      "end": 62,
      "score": 0.85,
      "analysis_explanation": {
        "recognizer": "SpacyRecognizer",
        "pattern_name": null,
        "pattern": null,
        "original_score": 0.85,
        "score": 0.85,
        "textual_explanation": "Identified as DATE by Spacy's Named Entity Recognition",
        "score_context_improvement": 0,
        "supportive_context_word": "",
        "validation_result": null
      },
      "recognition_metadata": {
        "recognizer_name": "SpacyRecognizer",
        "recognizer_identifier": "SpacyRecognizer_2348682647184"
      }
    }
  ]
}

```

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