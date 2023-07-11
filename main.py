import random
from fastapi import FastAPI
import uvicorn
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, RecognizerRegistry
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import EmailRecognizer, IpRecognizer, PhoneRecognizer, IbanRecognizer, CreditCardRecognizer, SpacyRecognizer

pii_app = FastAPI()


class PII:
    def __init__(self, lang: str, text: str, dummies: bool):
        triple_text = ''' 
        '''
        self.text = triple_text + text
        self.lang = lang
        self.dummies = dummies

        # model configuration for greek and english
        configuration = {"nlp_engine_name": "spacy",
                         "models": [{"lang_code": "el", "model_name": "el_core_news_lg"},
                                    {"lang_code": "en", "model_name": "en_core_web_lg"}]
                        }

        # NLP engine based on config
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine_el_en = provider.create_engine()

        #List of entities to look for
        self.entities = ['NUMBERS_en', 'NUMBERS_el', 'PERSON',
                         'EMAIL_ADDRESS', 'IP_ADDRESS',
                         'LOCATION']
        
        # Setting up greek recognizers
        email_recognizer_el = EmailRecognizer(supported_language="el", context=["μειλ"])
        ip_recognizer_el = IpRecognizer(supported_language="el", context=["ip", "IP"])
        phone_recognizer_el = PhoneRecognizer(supported_language="el", context=["τηλέφωνο", "τηλεφωνο", "αριθμός", "αριθμος"])
        iban_recognizer_el = IbanRecognizer(supported_language="el", context=["ιβαν", "iban", "τράπεζα", "τραπεζα"])
        credit_recognizer_el = CreditCardRecognizer(supported_language="el", context=["credit","card","visa","mastercard","cc",
                                                                                      "amex","discover","jcb","diners","maestro","instapayment",
                                                                                      "πιστωτική","πιστωτικη","κάρτα","καρτα"])
        spacy_recognizer_el = SpacyRecognizer(supported_language="el")
        numbers_pattern = Pattern(name="numbers_pattern",regex=r"\d+", score = 0.2)
        number_recognizer_en = PatternRecognizer(supported_entity="NUMBERS_en", patterns = [numbers_pattern],supported_language='en')
        number_recognizer_el = PatternRecognizer(supported_entity="NUMBERS_el", patterns = [numbers_pattern],supported_language='el')


        # Registry object along with predefined recognizers
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()

        # Adding custom recognizers to registry
        registry.add_recognizer(email_recognizer_el)
        registry.add_recognizer(ip_recognizer_el)
        registry.add_recognizer(phone_recognizer_el)
        registry.add_recognizer(iban_recognizer_el)
        registry.add_recognizer(number_recognizer_el)
        registry.add_recognizer(number_recognizer_en)
        registry.add_recognizer(credit_recognizer_el)
        registry.add_recognizer(spacy_recognizer_el)

        # Analyzer and anonymizer objects        
        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine_el_en, 
                                       supported_languages=["el", "en"],
                                       registry=registry)
        
        self.anonymizer = AnonymizerEngine()
        

        # Can define how the operators will behave for each entity. Depends on mode.
        if self.dummies == False:
            self.operators = {            
                "PERSON": OperatorConfig("replace", {"new_value": "<ANONYMOUS>"}),
                
                "NUMBERS_en": OperatorConfig("replace", {"new_value": "<HIDDEN_NUMBER>"}),

                "NUMBERS_el": OperatorConfig("replace", {"new_value": "<HIDDEN_NUMBER>"}),
                
                "IP_ADDRESS": OperatorConfig("mask", {"type": "mask","masking_char": "*",
                                                        "chars_to_mask": 12,
                                                        "from_end": True,}),
                                                                    
                "LOCATION": OperatorConfig("replace", {"new_value": "<HIDDEN_LOCATION>"}),
                
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<HIDDEN_EMAIL>"}),       
            }
        
        elif self.dummies == True:
             self.operators = {            
                "PERSON": OperatorConfig("replace", {"new_value": "John Smith"}),
                
                "NUMBERS_en": OperatorConfig("replace", {"new_value": "0000"}),

                "NUMBERS_el": OperatorConfig("replace", {"new_value": "0000"}),
                
                "IP_ADDRESS": OperatorConfig("mask", {"type": "mask","masking_char": "*",
                                                        "chars_to_mask": 12,
                                                        "from_end": True,}),
                                                                    
                "LOCATION": OperatorConfig("replace", {"new_value": random.choice(["Athens","Nicosia","New York"])}),
                
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "example@mail.com"})       
            }


    def anonymize(self):
        self.results = self.analyzer.analyze(text=self.text,
                                            entities=self.entities,
                                            language=self.lang,return_decision_process=True)
        
        self.anon_text = self.anonymizer.anonymize(text=self.text, analyzer_results=self.results,
                                            operators=self.operators) 
        print(self.anon_text.text)
    
    def array(self):
        entity_array = []
        for i in range(len(self.results)):
            entity_array.append(self.results[i].to_dict())
        print(entity_array)

@pii_app.get('/anon/{lang}/{text}/{mode}')
def anonymize_user_input(lang: str, text:str, mode:bool):
    user_input = PII(lang, text, mode)
    user_input.anonymize()
    return {'result': user_input.array()}



# anonymize_user_input('el', 'Με λένε Γιάννη. Mένω στο Ηράκλειο.',False)
# anonymize_user_input('en', 'My name is John. I live in Athens.', True)


if __name__ == "__main__":
    uvicorn.run(pii_app, host="0.0.0.0", port=8000)