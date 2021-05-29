import copy

from django.test import TestCase

from backend.models import ElectionSession, Election, Candidate, Eligibility
from skule_vote.tests import SetupMixin


class ElectionSessionAdminFormTestCase(SetupMixin, TestCase):
    """
    Tests the ElectionSessionAdminForm for the optimal cases when creating just an ElectionSession
    and/or ElectionSession with corresponding Elections, Candidates, and Eligibilities. Also tests
    the failure modes for that form and ensures that they are properly handled and displayed to the user.
    """

    def setUp(self, start_time_offset_days=1, end_time_offset_days=30):
        super().setUp()
        self._set_election_session_data()

    def test_no_csv_file_uploaded_creates_election_session(self):
        form = self._build_election_session_form()
        self.assertTrue(form.is_valid())
        instance = form.save()

        self.assertEqual(ElectionSession.objects.count(), 1)
        self.assertEqual(ElectionSession.objects.all()[0], instance)
        self.assertEqual(Election.objects.count(), 0)
        self.assertEqual(Candidate.objects.count(), 0)
        self.assertEqual(Eligibility.objects.count(), 0)

        self.assertEqual(
            ElectionSession.objects.all()[0].election_session_name,
            self.data["election_session_name"],
        )
        self.assertEqual(
            ElectionSession.objects.all()[0].start_time, self.data["start_time"]
        )
        self.assertEqual(
            ElectionSession.objects.all()[0].end_time, self.data["end_time"]
        )

    def test_all_csv_files_uploaded_creates_election_session_and_election_and_candidates_and_eligibilities(
        self,
    ):
        form = self._build_election_session_form(files=self._build_admin_csv_files())
        self.assertTrue(form.is_valid())
        instance = form.save()

        self.assertEqual(ElectionSession.objects.count(), 1)
        self.assertEqual(ElectionSession.objects.all()[0], instance)
        self.assertEqual(Election.objects.count(), 2)
        self.assertEqual(Candidate.objects.count(), 2)
        self.assertEqual(Eligibility.objects.count(), 2)

    def test_1_or_2_csv_files_uploaded_throws_validation_error(self):
        modified_csv_files = self._build_admin_csv_files()
        del modified_csv_files["upload_candidates"]

        form_1 = self._build_election_session_form(
            files=modified_csv_files
        )  # Two files uploaded
        self.assertFalse(form_1.is_valid())
        self.assertIn(
            "CSV Files for Elections, Candidates, and Eligibilities must all be uploaded all at once or none at all.",
            form_1.errors["__all__"],
        )

        del modified_csv_files["upload_elections"]
        form_2 = self._build_election_session_form(
            files=modified_csv_files
        )  # One file uploaded
        self.assertFalse(form_2.is_valid())
        self.assertIn(
            "CSV Files for Elections, Candidates, and Eligibilities must all be uploaded all at once or none at all.",
            form_2.errors["__all__"],
        )

        self.assertEqual(ElectionSession.objects.count(), 0)
        self.assertEqual(Election.objects.count(), 0)
        self.assertEqual(Candidate.objects.count(), 0)
        self.assertEqual(Eligibility.objects.count(), 0)

    def test_bad_headers_throws_validation_error(self):
        modified_headers = copy.deepcopy(self.header_definitions)
        modified_headers["elections"][0] = "election_names"
        modified_csv_files = self._build_admin_csv_files(header=modified_headers)
        form_1 = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form_1.is_valid())
        self.assertEqual(
            "Invalid header discovered. See more info below.",
            form_1.errors["__all__"][0],
        )
        self.assertIn(
            "Invalid header. Header for the Elections CSV must contain",
            form_1.errors["upload_elections"][0],
        )
        self.assertIn(
            f"Invalid header value found: [{modified_headers['elections'][0]}].",
            form_1.errors["upload_elections"][0],
        )

        modified_headers = copy.deepcopy(self.header_definitions)
        modified_headers["candidates"][0] = "nmaes"
        modified_csv_files = self._build_admin_csv_files(header=modified_headers)
        form_2 = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form_1.is_valid())
        self.assertEqual(
            "Invalid header discovered. See more info below.",
            form_2.errors["__all__"][0],
        )
        self.assertIn(
            "Invalid header. Header for the Candidates CSV must contain",
            form_2.errors["upload_candidates"][0],
        )
        self.assertIn(
            f"Invalid header value found: [{modified_headers['candidates'][0]}].",
            form_2.errors["upload_candidates"][0],
        )

        modified_headers = copy.deepcopy(self.header_definitions)
        modified_headers["eligibilities"][0] = "elections_names"
        modified_csv_files = self._build_admin_csv_files(header=modified_headers)
        form_3 = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form_1.is_valid())

        self.assertEqual(
            "Invalid header discovered. See more info below.",
            form_3.errors["__all__"][0],
        )
        self.assertIn(
            "Invalid header. Header for the Eligibilities CSV must contain",
            form_3.errors["upload_eligibilities"][0],
        )
        self.assertIn(
            f"Invalid header value found: [{modified_headers['eligibilities'][0]}].",
            form_3.errors["upload_eligibilities"][0],
        )

    def test_different_row_lengths_adds_error(self):
        modified_body = copy.deepcopy(self.body_definitions)
        modified_body["elections"][0].append("1")
        modified_body["candidates"][0].append("1")
        modified_body["eligibilities"][0].append("1")

        modified_csv_files = self._build_admin_csv_files(body=modified_body)

        form = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form.is_valid())

        self.assertEqual(
            "Invalid row length discovered. See more info below.",
            form.errors["__all__"][0],
        )
        self.assertIn(
            "[elections.csv] All rows in the CSV must be the same length as the header.",
            form.errors["upload_elections"][0],
        )
        self.assertIn(
            "[candidates.csv] All rows in the CSV must be the same length as the header.",
            form.errors["upload_candidates"][0],
        )
        self.assertIn(
            "[eligibilities.csv] All rows in the CSV must be the same length as the header.",
            form.errors["upload_eligibilities"][0],
        )

    def test_election_and_eligibility_csvs_different_length_adds_error(self):
        modified_body = copy.deepcopy(self.body_definitions)
        del modified_body["eligibilities"][1]

        modified_csv_files = self._build_admin_csv_files(body=modified_body)

        form = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form.is_valid())

        self.assertEqual(
            "Election and Eligibilities don't match. See more info below.",
            form.errors["__all__"][0],
        )
        self.assertIn(
            "[eligibilities.csv] Elections and Eligibilities CSVs must have the same number of rows. "
            f"Eligibilities CSV has {len(modified_body['eligibilities'])} rows.",
            form.errors["upload_eligibilities"][0],
        )

        self.assertIn(
            "[elections.csv] Elections and Eligibilities CSVs must have the same number of rows. "
            f"Elections CSV has {len(modified_body['elections'])} rows.",
            form.errors["upload_elections"][0],
        )

    def test_different_election_name_in_candidates_or_eligibilities_csvs_adds_error(
        self,
    ):
        modified_body = copy.deepcopy(self.body_definitions)
        modified_body["candidates"][0][1] = "1st Year Civil Engineering Rep"

        modified_csv_files = self._build_admin_csv_files(body=modified_body)

        form_1 = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form_1.is_valid())

        self.assertEqual(
            "Election names don't match over all CSV files.",
            form_1.errors["__all__"][0],
        )
        self.assertIn(
            f"[elections.csv, candidates.csv] Election names within the Candidates CSV must match "
            f"those within the Elections CSV. Invalid Election name discovered: {modified_body['candidates'][0][1]}",
            form_1.errors["upload_candidates"][0],
        )

        modified_body = copy.deepcopy(self.body_definitions)
        modified_body["eligibilities"][1][0] = "4th Year Char"

        modified_csv_files = self._build_admin_csv_files(body=modified_body)

        form_2 = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form_2.is_valid())

        self.assertEqual(
            "Election names don't match over all CSV files.",
            form_2.errors["__all__"][0],
        )
        self.assertIn(
            f"[elections.csv, eligibilities.csv] Election names within the Eligibilities CSV must match "
            f"those within the Elections CSV. Invalid Election name discovered: {modified_body['eligibilities'][1][0]}",
            form_2.errors["upload_eligibilities"][0],
        )

    def test_election_seats_nan_adds_error(self):
        modified_body = copy.deepcopy(self.body_definitions)
        modified_body["elections"][0][1] = "f"

        modified_csv_files = self._build_admin_csv_files(body=modified_body)

        form = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form.is_valid())

        self.assertIn(
            f"seats_available for each election must be an integer.",
            form.errors["upload_elections"][0],
        )

    def test_election_seats_less_than_1_adds_error(self):
        modified_body = copy.deepcopy(self.body_definitions)
        modified_body["elections"][0][1] = "0"

        modified_csv_files = self._build_admin_csv_files(body=modified_body)

        form = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form.is_valid())

        self.assertIn(
            f"seats_available for each election must be >=1.",
            form.errors["upload_elections"][0],
        )

    def test_election_category_not_in_choices_adds_error(self):
        modified_body = copy.deepcopy(self.body_definitions)

        modified_body["elections"][0][2] = "Class Rap"
        modified_csv_files = self._build_admin_csv_files(body=modified_body)

        form = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form.is_valid())

        self.assertIn(
            f"Incorrect election category found in CSV: [Class Rap].",
            form.errors["upload_elections"][0],
        )

    def test_eligibilities_eligibile_fields_not_1_or_0_adds_error(self):
        modified_body = copy.deepcopy(self.body_definitions)
        modified_body["eligibilities"][1][1] = "4"

        modified_csv_files = self._build_admin_csv_files(body=modified_body)

        form_1 = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form_1.is_valid())

        self.assertIn(
            f"[eligibilities.csv] Eligibilities must be true/false values represented by the *integer* values of "
            f"1 or 0. Non-integer value found in CSV: [4].",
            form_1.errors["upload_eligibilities"][0],
        )

        modified_body = copy.deepcopy(self.body_definitions)
        modified_body["eligibilities"][1][1] = "f"

        modified_csv_files = self._build_admin_csv_files(body=modified_body)

        form_2 = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form_2.is_valid())

        self.assertIn(
            f"[eligibilities.csv] Eligibilities must be true/false values represented by the *integer* values "
            f"of 1 or 0. Non-integer value found in CSV: [f].",
            form_2.errors["upload_eligibilities"][0],
        )

    def test_eligibilities_status_field_not_in_choices_adds_error(self):
        modified_body = copy.deepcopy(self.body_definitions)
        modified_body["eligibilities"][1][16] = "Full Time and Part Time"

        modified_csv_files = self._build_admin_csv_files(body=modified_body)

        form = self._build_election_session_form(files=modified_csv_files)
        self.assertFalse(form.is_valid())

        self.assertIn(
            f"[eligibilities.csv] Eligibility status category must be one of: [Full Time, Part Time, "
            f"Full and Part Time]. Incorrect category found in CSV: [{modified_body['eligibilities'][1][16]}].",
            form.errors["upload_eligibilities"][0],
        )
