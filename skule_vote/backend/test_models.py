from django.test import TestCase

from backend.models import Election
from skule_vote.tests import SetupMixin


class ElectionModelTestCase(SetupMixin, TestCase):
    """
    Tests the Election model. Makes sure any overloaded functions work properly.
    """

    def setUp(self):
        super().setUp()
        self._set_election_session_data()

    def test_election_created_also_creates_ron_candidate(self):
        election_session = self._create_election_session(self.data)
        self.setUpElections(election_session)

        for election in Election.objects.all():
            self.assertEqual(election.candidates.count(), 1)
            for candidate in election.candidates.all():
                self.assertEqual(candidate.name, "Reopen Nominations")
