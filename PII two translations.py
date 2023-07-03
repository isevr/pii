import translators as ts
import translators.server as tss
from presidio_analyzer import AnalyzerEngine, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorResult, OperatorConfig
from presidio_analyzer import PatternRecognizer

class Tran:
    def __init__(self, lang, text):
        self.text = text
        self.lang = lang

        #List of entities to look for
        self.entities = ['PERSON', 'NUMBERS',
                   'EMAIL_ADDRESS', 'IP_ADDRESS', 'NRP',
                   'LOCATION', 'BLOOD_TYPE']
        
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # Option to create custom recognizers
        blood_type_recognizer = PatternRecognizer(supported_entity="BLOOD_TYPE",
                                      deny_list=["A-","A+","B-","B+","AB-","AB+","O-","O+"])
        
        numbers_pattern = Pattern(name="numbers_pattern",regex="\d+", score = 0.3)

        number_recognizer = PatternRecognizer(supported_entity="NUMBERS", patterns = [numbers_pattern])

        self.analyzer.registry.add_recognizer(blood_type_recognizer)
        self.analyzer.registry.add_recognizer(number_recognizer)

        # Can define how the operators will behave for each entity
        self.operators = {
            "DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"}),
            
            "PERSON": OperatorConfig("replace", {"new_value": "<ANONYMOUS>"}),
            
            "NUMBERS": OperatorConfig("replace", {"new_value": "<HIDDEN_NUMBER>"}),
            
            "IP_ADDRESS": OperatorConfig("mask", {"type": "mask","masking_char": "*",
                                                    "chars_to_mask": 5,
                                                    "from_end": True,}),
            "NRP": OperatorConfig("replace", {"new_value": "<REDACTED_NRP>"}),
            
            "LOCATION": OperatorConfig("replace", {"new_value": "<HIDDEN_LOCATION>"}),
            
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<HIDDEN_EMAIL>"}),
            
            "BLOOD_TYPE": OperatorConfig("replace", {"new_value": "<HIDDEN_BLOOD_TYPE>"})
        
        }
    
    def translate(self):
        #translates from greek to english 
        self.translated_txt = ts.translate_text(self.text, translator='google',
                                            from_language='el',
                                            to_language='en')
        return self.translated_txt


    def anonymize(self):
                
        if self.lang == 'el':
        # Anonymize the translated text
            self.results = self.analyzer.analyze(text=self.translated_txt,
                                                entities=self.entities,
                                                language='en')
            self.anon_text = self.anonymizer.anonymize(text=self.translated_txt, analyzer_results=self.results,
                                                operators=self.operators)
            return self.anon_text
        
        #Anonymize english text
        elif self.lang == 'en':
            self.results = self.analyzer.analyze(text=self.text,
                                                entities=self.entities,
                                                language='en')
            self.anon_text = self.anonymizer.anonymize(text=self.text, analyzer_results=self.results,
                                                operators=self.operators)
            return self.anon_text
        
    def PII_removal_from_original(self):
        start = self.results[0].to_dict().get('start')
        end = self.results[0].to_dict().get('end')

        if self.lang == 'el':
            pii_translated = ts.translate_text(self.anon_text.text, translator='google',
                                           from_language='en',to_language='el')
        
            return pii_translated
        
        if self.lang == 'en':
            return self.anon_text.text


def process_user_input():

    languages = ['el','en']
    exit_phrases = ['goodbye','bye','good bye','see you']
    

    lang_input = str(input('Choose language: \n\
    1) Greek \n\
    2) English \n'))
    if lang_input.lower() == 'greek' or lang_input == "1":
        chosen_lang = languages[0]
    elif lang_input.lower() == 'english' or lang_input == "2":
        chosen_lang = languages[1]
    else:
        print('Language not supported')

    while True:
        global user_tran
        user_input = str(input(f'Say something personal: '))
        user_tran = Tran(chosen_lang, user_input)

        if chosen_lang == 'el':
            user_tran.translate()

        if user_tran.text.lower() in exit_phrases:
            print('Goodbye!')
            break

        user_tran.anonymize()
        
        print(user_tran.PII_removal_from_original())

process_user_input()
