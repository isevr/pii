from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, RecognizerRegistry
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import EmailRecognizer, IpRecognizer, PhoneRecognizer, IbanRecognizer, CreditCardRecognizer, SpacyRecognizer

class Tran:
    def __init__(self, lang, text):
        triple_text = ''' 
        '''
        self.text = triple_text + text
        self.lang = lang

        # model configuration for greek and english
        configuration = {"nlp_engine_name": "spacy",
                         "models": [{"lang_code": "el", "model_name": "el_core_news_lg"},
                                    {"lang_code": "en", "model_name": "en_core_web_lg"}]
                        }

        # NLP engine based on config
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine_el_en = provider.create_engine()

        #List of entities to look for
        self.entities = ['NUMBERS', 'PERSON',
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
        numbers_pattern = Pattern(name="numbers_pattern",regex=r"\d+", score = 0.1)
        number_recognizer = PatternRecognizer(supported_entity="NUMBERS", patterns = [numbers_pattern],supported_language='el')

        # Registry object along with predefined recognizers
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()

        # Adding custom recognizers to registry
        registry.add_recognizer(email_recognizer_el)
        registry.add_recognizer(ip_recognizer_el)
        registry.add_recognizer(phone_recognizer_el)
        registry.add_recognizer(iban_recognizer_el)
        registry.add_recognizer(number_recognizer)
        registry.add_recognizer(credit_recognizer_el)
        registry.add_recognizer(spacy_recognizer_el)

        # Analyzer and anonymizer objects        
        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine_el_en, 
                                       supported_languages=["el", "en"],
                                       registry=registry)
        
        self.anonymizer = AnonymizerEngine()
        

        # Can define how the operators will behave for each entity
        self.operators = {            
            "PERSON": OperatorConfig("replace", {"new_value": "<ANONYMOUS>"}),
            
            "NUMBERS": OperatorConfig("replace", {"new_value": "<HIDDEN>"}),
            
            "IP_ADDRESS": OperatorConfig("mask", {"type": "mask","masking_char": "*",
                                                    "chars_to_mask": 12,
                                                    "from_end": True,}),
                                                                
            "LOCATION": OperatorConfig("replace", {"new_value": "<HIDDEN>"}),
            
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<HIDDEN_EMAIL>"})       
        }


    def anonymize(self):
        self.results = self.analyzer.analyze(text=self.text,
                                            entities=self.entities,
                                            language=self.lang)
        
        self.anon_text = self.anonymizer.anonymize(text=self.text, analyzer_results=self.results,
                                            operators=self.operators) 
        print(self.anon_text.text)
    
    def array(self):
        entity_matrix = {}
        for i in range(len(self.results)):
            entity_matrix[self.results[i].to_dict()['entity_type']] = self.text[self.results[i].to_dict()['start']:self.results[i].to_dict()['end']]
        print(entity_matrix)

def anonymize_user_input(lang, text):
    user_input = Tran(lang, text)
    user_input.anonymize()
    return user_input.array()

anonymize_user_input('el', 'Με λένε Γιάννη. Mένω στο Ηράκλειο.')
anonymize_user_input('en', 'My name is John. I live in Athens.')
