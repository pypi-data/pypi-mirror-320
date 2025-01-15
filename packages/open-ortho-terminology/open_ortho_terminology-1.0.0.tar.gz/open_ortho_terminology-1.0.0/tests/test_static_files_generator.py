import unittest
from pathlib import Path
import json
import os

from terminology.main import save_code_system_to_fhir
from terminology.resources.code_systems import extraoral_2d_photographic_vews 

class TestSaveCodeSystemToFhir(unittest.TestCase):

    def test_save_code_system_to_fhir(self):
        module = extraoral_2d_photographic_vews
        filename = Path('test_output.json')

        # Call the function
        save_code_system_to_fhir(module, filename)

        # Verify the file was created
        self.assertTrue(filename.exists())

        # Verify the content of the file
        with open(filename, 'r') as f:
            data = json.load(f)
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0)
            self.assertEqual(data[0]['resourceType'], 'CodeSystem')

        # Clean up
        os.remove(filename)

if __name__ == '__main__':
    unittest.main()