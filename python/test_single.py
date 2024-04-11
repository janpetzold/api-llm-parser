# This script is just a helper script to quickly execute a single test on a hard-coded model.

import unittest
from api_parser import analyze_with_llm

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


class TestApiParser(unittest.TestCase):
    def test_analyze_default(self):
        result = analyze_with_llm("phi-2", default_context, default_prompt)
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

if __name__ == '__main__':
    unittest.main()