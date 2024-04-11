# Test suite to run all tests on all models

import unittest
import re
from api_parser import analyze_with_llm

current_llm = None

default_context = """You are a system assistant that helps to support APIs with their correct parameters. 
        Please extract the needed data from the user input and always return it in the same format as defined here.
        NAME: <User name that was identified>
        MAIL: <User e-mail address that was identified. It should be validated to match common standard RFC 5322.>
        ADDRESS: <Postal address that was identified>
        ZIP: <Zip or postal code that was identified based on address, location and country>
        LOCATION: <Location that was identified> 
        COUNTRY: <Country identified based on location and address in ISO-3166-1 two-letter standard>
        REQUEST: <Actual request of the user that was identified. Can be either Order, Complaint or Info.>
        PRODUCT: <Product the user refers to as it was identified>
        DATE: <Date that was identified in ISO8601 format>
        GPS: <Latitude and Longitude based on location>
        TIMEZONE: <Timezone based on users location. Should match the timezone value defined in IANA/Olson database.>
        In case you were not able to retrieve some parameter or the user did not provide it please return that value
        as "Unknown", so for example if the GPS coordinates can't be retrieved the response shall be GPS: Unknown."""

default_prompt = """Hello world, this is a great product so I'd like to order the Hummingbird 42. I am Jan from Berlin, 
        I'd like to be this shipped by 12th of August 2026 and my mail address is jan@foo.com and my address is 
        Mollstrasse 1 in 10117."""

def run_tests_with_config(config):
    global current_llm
    current_llm = config
    
     # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test cases from current class to the suite
    suite.addTest(unittest.makeSuite(TestApiParser))
    
    # Create a test runner that will execute the test suite
    runner = unittest.TextTestRunner()
    print(f"\nRunning tests with configuration: {config}")
    runner.run(suite)

def validate_gps_string(gps_string: str) -> bool:
    # Extract latitude and longitude from the input string
    match = re.match(r"GPS:\s*(-?\d+\.\d+),(-?\d+\.\d+)", gps_string)
    if not match:
        return False

    latitude, longitude = float(match.group(1)), float(match.group(2))

    # Check if latitude /longitude is around 52.XXX / 13.YYY which would be Berlin/Germany
    valid_latitude = 51 <= latitude <= 53
    valid_longitude = 12 <= longitude <= 14

    return valid_latitude and valid_longitude

class TestApiParser(unittest.TestCase):
    def test_analyze_default(self):
        result = analyze_with_llm(current_llm, default_context, default_prompt)
        self.assertIn("NAME: Jan", result)
        self.assertIn("MAIL: jan@foo.com", result)
        self.assertIn("ADDRESS: Mollstrasse 1", result)
        self.assertIn("ZIP: 10117", result)
        self.assertIn("LOCATION: Berlin", result)
        self.assertIn("COUNTRY: DE", result)
        self.assertIn("REQUEST: Order", result)
        self.assertIn("PRODUCT: Hummingbird 42", result)
        self.assertIn("DATE: 2026-08-12", result)
        self.assertIn("TIMEZONE: Europe/Berlin", result)

    def test_analyze_gps(self):
        result = analyze_with_llm(current_llm, default_context, default_prompt)
        self.assertNotIn("GPS: Unknown", result)

        # Get GPS String
        match = re.search(r"GPS:.*", result, re.IGNORECASE)
        if match:
            gps_value = match.group()
            self.assertTrue(validate_gps_string(gps_value))
        else:
            self.fail("GPS value not found")

    def test_analyze_small_town(self):
        # Check small town of https://en.wikipedia.org/wiki/Len%C3%A7%C3%B3is Brazil
        prompt = """Hello world, this is a great product so I'd like to order the Hummingbird 42. I am Jan from Lençóis, 
        I'd like to be this shipped by 12th of August 2026 and my mail address is jan@foo.com and my address is 
        Rua José Florêncio 11 in 469600-000."""

        result = analyze_with_llm(current_llm, default_context, prompt)

        self.assertIn("ADDRESS: Rua José Florêncio 11", result)
        self.assertIn("ZIP: 469600-000", result)
        self.assertIn("LOCATION: Lençóis", result)
        self.assertIn("COUNTRY: BR", result)
        self.assertIn("TIMEZONE: America/Bahia", result)
    
    def test_missing_product(self):
        prompt = """Hello world, this is a great product so I'd like to order. I am Jan from Berlin, 
        I'd like to be this shipped by 12th of August 2026 and my mail address is jan@foo.com and my address is 
        Mollstrasse 1 in 10117."""

        result = analyze_with_llm(current_llm, default_context, prompt)

        self.assertIn("PRODUCT: Unknown", result)

    def test_language_german(self):
        prompt = """Hallo, dieses Produkt sieht nützlich aus, ich möchte das Hummingbird 42 gern bestellen.
        Ich bin Jan aus Berlin, der Versand soll bis zum 12.August 2026 erfolgen. Meine Mailadresse ist 
        jan@foo.com und meine Postanschrift die Mollstrasse 1 in 10117 Berlin."""

        result = analyze_with_llm(current_llm, default_context, prompt)
        self.assertIn("NAME: Jan", result)
        self.assertIn("MAIL: jan@foo.com", result)
        self.assertIn("ADDRESS: Mollstrasse 1", result)
        self.assertIn("ZIP: 10117", result)
        self.assertIn("LOCATION: Berlin", result)
        self.assertIn("COUNTRY: DE", result)
        self.assertIn("REQUEST: Order", result)
        self.assertIn("PRODUCT: Hummingbird 42", result)
        self.assertIn("DATE: 2026-08-12", result)
        self.assertIn("TIMEZONE: Europe/Berlin", result)

    def test_language_romanian(self):
        prompt = """Buna ziua, acest produs pare util, as dori sa comand Hummingbird 42.
         Sunt Jan din Romania, expedierea ar trebui să aibă loc până pe 12 august 2026. Adresa mea de e-mail este
         jan@foo.com și adresa mea poștală este Strada Tudor Vladimirescu 12 în Sinaia 106100."""

        result = analyze_with_llm(current_llm, default_context, prompt)
        self.assertIn("NAME: Jan", result)
        self.assertIn("MAIL: jan@foo.com", result)
        self.assertIn("ADDRESS: Strada Tudor Vladimirescu 12", result)
        self.assertIn("ZIP: 106100", result)
        self.assertIn("LOCATION: Sinaia", result)
        self.assertIn("COUNTRY: RO", result)
        self.assertIn("REQUEST: Order", result)
        self.assertIn("PRODUCT: Hummingbird 42", result)
        self.assertIn("DATE: 2026-08-12", result)
        self.assertIn("TIMEZONE: Europe/Bucharest", result)

    def test_invalid_request_type(self):
        prompt = """Hello world, I am not sure what I want here regarding the Hummingbird 42 but I am writing anyway
        just to waste a little of your time. I am Jan from Berlin, my favourite date of them all is 12th of August 2026 
        and my mail address is jan@foo.com and my address is Mollstrasse 1 in 10117."""
        
        result = analyze_with_llm(current_llm, default_context, prompt)

        self.assertIn("REQUEST: Unknown", result)

    def test_typos(self):
        prompt = """Hello world, this is a great product so I'd like to oder the Hummingbird 42. I am Jan from Brli9n (capital 
        of Germany), I'd like to be this shipped by 34th of August 2026 and my mail address is jan-at-foo.com and my address is 
        Mollstrasse 1 in 10117."""

        result = analyze_with_llm(current_llm, default_context, prompt)

        self.assertIn("MAIL: jan@foo.com", result)
        self.assertIn("LOCATION: Berlin", result)
        self.assertIn("COUNTRY: DE", result)
        self.assertIn("REQUEST: Order", result)
        self.assertIn("DATE: Unknown", result)
        self.assertIn("TIMEZONE: Europe/Berlin", result)

    def test_complaint(self):
        prompt = """Hello world, I am very unhappy with the Hummingbird 42. I turned it on and all I see is some
        flashing LED and that is it. Power supply seems to be working. I am Jan from Berlin and ordered the
        product on 10th of October 2021 and my mail address is jan@foo.com."""

        result = analyze_with_llm(current_llm, default_context, prompt)

        self.assertIn("MAIL: jan@foo.com", result)
        self.assertIn("PRODUCT: Hummingbird 42", result)
        self.assertIn("REQUEST: Complaint", result)
        self.assertIn("DATE: 2021-10-10", result)
    
    def test_swap_mail_and_email(self):
        prompt = """Hello world, this is a great product so I'd like to order the Hummingbird 42. I am Jan from Berlin, 
        I'd like to be this shipped by 12th of August 2026 and you can send it to jan@foo.com. My mail address is 
        Mollstrasse 1 in 10117."""

        result = analyze_with_llm(current_llm, default_context, prompt)

        self.assertIn("MAIL: jan@foo.com", result)
        self.assertIn("PRODUCT: Hummingbird 42", result)
        self.assertIn("REQUEST: Order", result)
        self.assertIn("ADDRESS: Mollstrasse 1", result)
        self.assertIn("ZIP: 10117", result)
        self.assertIn("LOCATION: Berlin", result)
        self.assertIn("COUNTRY: DE", result)

if __name__ == '__main__':
    #for config in ['gpt-4-turbo-2024-04-09', 'gpt-3.5-turbo-0125', 'llama-2-7b-chat-fp16', 'phi-2', 'gemma-7b-it', 'mistral-7b-instruct-v0.2', 'mistral.mistral-large-2402-v1:0', 'anthropic.claude-3-sonnet-20240229-v1:0', 'meta.llama2-13b-chat-v1', 'meta.llama2-70b-chat-v1']:
    for config in ['llama-2-7b-chat-fp16', 'phi-2', 'gemma-7b-it', 'mistral-7b-instruct-v0.2']:
        run_tests_with_config(config)