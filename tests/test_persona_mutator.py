import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import unittest

from persona_mutator import PersonaMutator


class TestPersonaMutator(unittest.TestCase):
    def setUp(self):
        self.mutator = PersonaMutator()
        self.base_file = os.path.join('personas', 'manifestos', 'companion.json')
        self.base_persona = self.mutator.load_persona(self.base_file)

    def test_mutation_generates_changes(self):
        mutated = self.mutator.mutate(self.base_persona, intensity='radical')
        self.assertEqual(mutated['metadata']['parent_id'], self.base_persona['id'])
        changed = mutated.get('response_temperature') is not None or \
                  mutated.get('preferred_handler') is not None or \
                  mutated.get('response_length') != self.base_persona.get('response_length') or \
                  mutated.get('prompt_style', {}).get('tone') != self.base_persona.get('prompt_style', {}).get('tone')
        self.assertTrue(changed)

    def test_save_mutation(self):
        mutated = self.mutator.mutate(self.base_persona, intensity='light')
        path = self.mutator.save_mutation(mutated, self.base_persona['id'])
        self.assertTrue(os.path.exists(path))
        with open(path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        self.assertEqual(loaded['metadata']['parent_id'], self.base_persona['id'])
        os.remove(path)


if __name__ == '__main__':
    unittest.main()
