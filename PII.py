import translators as ts
import translators.server as tss
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorResult, OperatorConfig
from presidio_analyzer import PatternRecognizer


class Tran:
    def __init__(self, lang, text):
        self.text = text
        self.lang = lang
    
    def translate(self):
        #translates from greek to english 
        self.translated_txt = ts.translate_text(self.text, translater='google',
                                            from_language='el',
                                            to_language='en')
        return self.translated_txt


    def anonymize(self):
        #List of entities to look for
        entities = ['PERSON','PHONE_NUMBER','CREDIT_CARD',
                   'EMAIL_ADDRESS', 'IP_ADDRESS', 'NRP',
                   'LOCATION', 'BLOOD_TYPE']
        
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # Option to create custom recognizers
        blood_type_recognizer = PatternRecognizer(supported_entity="BLOOD_TYPE",
                                      deny_list=["A-","A+","B-","B+","AB-","AB+","O-","O+"])

        self.analyzer.registry.add_recognizer(blood_type_recognizer)

        # Can define how the operators will behave for each entity
        operators = {
            "DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"}),
            
            "PERSON": OperatorConfig("replace", {"new_value": "<ANONYMOUS>"}),
            
            "CREDIT_CARD": OperatorConfig("mask",{"type":"mask","masking_char": "*",
                                                 "chars_to_mask": 12,
                                                 "from_end": True}),
            
            "PHONE_NUMBER": OperatorConfig("mask", {"type": "mask","masking_char": "*",
                                                    "chars_to_mask": 8,
                                                    "from_end": False,}),
            
            "IP_ADDRESS": OperatorConfig("mask", {"type": "mask","masking_char": "*",
                                                    "chars_to_mask": 12,
                                                    "from_end": True,}),
            "NRP": OperatorConfig("redact"),
            
            "LOCATION": OperatorConfig("replace", {"new_value": "<HIDDEN>"}),
            
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<HIDDEN_EMAIL>"}),
            
            "BLOOD_TYPE": OperatorConfig("replace", {"new_value": "<HIDDEN_BLOOD_TYPE>"})
        
        }
        
        if self.lang == 'el':
        # Anonymize the translated text
            self.results = self.analyzer.analyze(text=self.translated_txt,
                                                entities=entities,
                                                language='en')
            self.anon_text = self.anonymizer.anonymize(text=self.translated_txt, analyzer_results=self.results,
                                                operators=operators)
            return self.anon_text.text
        
        #Anonymize english text
        if self.lang == 'en':
            self.results = self.analyzer.analyze(text=self.text,
                                                entities=entities,
                                                language='en')
            self.anon_text = self.anonymizer.anonymize(text=self.text, analyzer_results=self.results,
                                                operators=operators)
            return self.anon_text.text
        
    def PII_removal_from_original(self):


        
def process_user_input():

    languages = ['el','en']
    exit_phrases = ['goodbye','bye','good bye','see you']
    chatbot_prompts = ['What is your name?', 'I need your credit card number to make this purchase',
                       'What email address should I send this to?', 'Tell me about yourself',
                       'What number should they call you at?', 'Where do you live?',
                       'What is your blood type?','What IP address are you connected from?']

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
        user_input = str(input(f'{random.choice(chatbot_prompts)}: '))
        user_tran = Tran(chosen_lang, user_input)
        user_tran.translate()
        if user_tran.translated_txt.lower() in exit_phrases:
            print('Goodbye!')
            break
        user_tran.anonymize()
        print(user_tran.tran_back())