import random
from fastapi import FastAPI
import uvicorn
# from mangum import Mangum
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, RecognizerRegistry
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import EmailRecognizer, IpRecognizer, PhoneRecognizer, IbanRecognizer, CreditCardRecognizer, SpacyRecognizer, DateRecognizer
from string import ascii_lowercase

app = FastAPI()
# handler = Mangum(app)

@app.get("/")
def read_root():
   return {"Welcome to": "PII-Anonymizer"}

@app.get('/anon/{lang}/{return_dummies}/{return_array}/-/{text:path}')
def anonymize(lang: str, return_dummies: bool, return_array: bool, text: str):
    # Check for full stop
    if text[-1] != '.':
        text = text+str('.')

    text = text.replace('-', '.')
    text = text.replace('/','.')


    # model configuration for greek and english
    configuration = {"nlp_engine_name": "spacy",
                        "models": [{"lang_code": "el", "model_name": "el_core_news_lg"},
                                   {"lang_code": "en", "model_name": "en_core_web_lg"}]
                    }

    # NLP engine based on config
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine_el_en = provider.create_engine()

    #List of entities to look for
    entities = ['PHONES_en', 'PHONES_el', 'PERSON',
                'LONG_NUMBERS_en', 'LONG_NUMBERS_el',
                'EMAIL_ADDRESS', 'IP_ADDRESS',
                'LOCATION', 'DATE_TIME', 'IBAN_CODE',
                'CREDIT_CARD']

    # Setting up greek recognizers
    email_recognizer_el = EmailRecognizer(supported_language="el", context=["μειλ"])
    ip_recognizer_el = IpRecognizer(supported_language="el", context=["ip", "IP"])
    phone_recognizer_el = PhoneRecognizer(supported_language="el", context=["τηλέφωνο", "τηλεφωνο", "αριθμός", "αριθμος"])
    iban_recognizer_el = IbanRecognizer(supported_language="el", context=["ιβαν", "iban", "τράπεζα", "τραπεζα"])
    credit_recognizer_el = CreditCardRecognizer(supported_language="el", context=["credit","card","visa","mastercard","cc",
                                                                                  "amex","discover","jcb","diners","maestro","instapayment",
                                                                                  "πιστωτική","πιστωτικη","κάρτα","καρτα"])
    spacy_recognizer_el = SpacyRecognizer(supported_language="el", context=['ετων','χρονων','γεννηθηκα','ετών','χρονών','γεννήθηκα'])
    date_recognizer_el = DateRecognizer(supported_language='el', context=['ετων','χρονων','γεννηθηκα','ετών','χρονών','γεννήθηκα'])

    #Custom recognizers
    phones_pattern = Pattern(name="phones_pattern",regex=r"(\+\d{6,})|(00\d{6,})", score=0.9) #regex to match: 1) at least 6 numbers after +, 2)at least 6 numbers after '00'
    custom_phone_recognizer_en = PatternRecognizer(supported_entity="PHONES_en", patterns = [phones_pattern],supported_language='en')
    custom_phone_recognizer_el = PatternRecognizer(supported_entity="PHONES_el", patterns = [phones_pattern],supported_language='el')

    long_numbers_pattern = Pattern(name='long_numbers_pattern', regex=r"\d{10,}", score=0.80) #regex to match at least 10 consecutive numbers
    long_numbers_recognizer_en = PatternRecognizer(supported_entity='LONG_NUMBERS_en', patterns=[long_numbers_pattern],supported_language='en')
    long_numbers_recognizer_el = PatternRecognizer(supported_entity='LONG_NUMBERS_el', patterns=[long_numbers_pattern],supported_language='el')


    # Registry object along with predefined recognizers
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()

    # Adding custom recognizers to registry
    registry.add_recognizer(email_recognizer_el)
    registry.add_recognizer(ip_recognizer_el)
    registry.add_recognizer(phone_recognizer_el)
    registry.add_recognizer(iban_recognizer_el)
    registry.add_recognizer(custom_phone_recognizer_en)
    registry.add_recognizer(custom_phone_recognizer_el)
    registry.add_recognizer(credit_recognizer_el)
    registry.add_recognizer(spacy_recognizer_el)
    registry.add_recognizer(long_numbers_recognizer_en)
    registry.add_recognizer(long_numbers_recognizer_el)
    registry.add_recognizer(date_recognizer_el)


    # Analyzer and anonymizer objects        
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine_el_en, 
                              supported_languages=["el", "en"],
                              registry=registry)

    anonymizer = AnonymizerEngine()


    # Can define how the operators will behave for each entity. Depends on dummies mode.
    if return_dummies == False:
        operators = {            
            "PERSON": OperatorConfig("replace", {"new_value": "ANONYMOUS"}),
            
            "PHONES_en": OperatorConfig("replace", {"new_value": "HIDDEN_PHONE_NUMBER"}),

            "PHONES_el": OperatorConfig("replace", {"new_value": "HIDDEN_PHONE_NUMBER"}),
            
            "IP_ADDRESS": OperatorConfig("mask", {"type": "mask","masking_char": "*","chars_to_mask": 5,"from_end": True,}),

            "LONG_NUMBERS_en": OperatorConfig("replace", {"new_value": "HIDDEN_LONG_NUMBER"}),

            "LONG_NUMBERS_el": OperatorConfig("replace", {"new_value": "HIDDEN_LONG_NUMBER"}),

            "LOCATION": OperatorConfig("replace", {"new_value": "HIDDEN_LOCATION"}),
            
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "HIDDEN_EMAIL"}),

            "DATE_TIME": OperatorConfig("replace", {"new_value": "HIDDEN_DATE_TIME"}),

            "CREDIT_CARD": OperatorConfig("replace", {"new_value": "HIDDEN_CREDIT_CARD"}),

            "IBAN_CODE": OperatorConfig("replace", {"new_value": "HIDDEN_IBAN"})

            }

    elif return_dummies == True:
        operators = {
            "PERSON": OperatorConfig("replace", {"new_value": "Anonymous"}),
        
            "PHONES_en": OperatorConfig("replace", {"new_value": "123456"}),

            "PHONES_el": OperatorConfig("replace", {"new_value": "123456"}),
        
            "IP_ADDRESS": OperatorConfig("replace", {"new_value": "127.0.0.1"}),

            "LONG_NUMBERS_en": OperatorConfig("replace", {"new_value": "0000000000"}),

            "LONG_NUMBERS_el": OperatorConfig("replace", {"new_value": "0000000000"}),
                                                            
            "LOCATION": OperatorConfig("replace", {"new_value": "Generic Location"}),
        
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "example@mail.com"}),

            "DATE_TIME": OperatorConfig("replace", {"new_value": "HIDDEN Date or Time"}),

            "CREDIT_CARD": OperatorConfig("replace", {"new_value": "0000 0000 0000 0000"}),

            "IBAN_CODE": OperatorConfig("replace", {"new_value": str(''.join(random.sample(ascii_lowercase.upper(),2)))+str('0'*32)})
            
            }
    results = analyzer.analyze(text=text,
                               entities=entities,
                               language=lang,return_decision_process=True)

    anon_text = anonymizer.anonymize(text=text, analyzer_results=results,
                                     operators=operators)
    
    # Returns array based on array mode chosen
    if return_array == True:
        entity_array = []
        for i in range(len(results)):
            entity_array.append(results[i].to_dict())
        return {'Anonymized text': anon_text.text, 
                'Entity Array': entity_array}
    
    elif return_array == False:
        return anon_text.text




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)


