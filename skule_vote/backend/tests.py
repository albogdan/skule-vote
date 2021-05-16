from backend.models import ElectionSession
from django.test import TestCase

# Create your tests here.
class FixturesTestCase(TestCase):
    fixtures = ["test_data.json"]

    def test_loaded_election_sessions(self):
        self.assertEqual(ElectionSession.objects.count(), 2)