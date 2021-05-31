import csv
from datetime import datetime
import io

from django import forms
from django.conf import settings

from backend.models import Candidate, ElectionSession, Election, Eligibility


def _now():
    return datetime.now().astimezone(settings.TZ_INFO)


class ElectionSessionAdminForm(forms.ModelForm):
    """
    Provides functionality for uploading CSV files which contain data for
    Elections, Candidates, and Eligibilities for that ElectionSession.
    This data is then checked for validity (formatting and logic) and then Elections,
    Candidates, and Eligibilities are created for that ElectionSession.
    """

    upload_elections = forms.FileField(required=False, allow_empty_file=True)
    upload_candidates = forms.FileField(required=False, allow_empty_file=True)
    upload_eligibilities = forms.FileField(required=False, allow_empty_file=True)

    class Meta:
        model = ElectionSession
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        # Initialize the parent class
        super(ElectionSessionAdminForm, self).__init__(*args, **kwargs)

        self.file_upload_list = None

        self.header_definitions = {
            "elections": ["election_name", "seats_available", "category"],
            "candidates": ["name", "election_name", "statement"],
            "eligibilities": [
                "election_name",
                "eng_eligible",
                "che_eligible",
                "civ_eligible",
                "ele_eligible",
                "cpe_eligible",
                "esc_eligible",
                "ind_eligible",
                "lme_eligible",
                "mec_eligible",
                "mms_eligible",
                "year_1_eligible",
                "year_2_eligible",
                "year_3_eligible",
                "year_4_eligible",
                "pey_eligible",
                "status_eligible",
            ],
        }

        # Define fields that should be read-only after the ElectionSession has started
        self.read_only_fields = [
            {
                "field_name": "election_session_name",
                "help_text": "ElectionSession name cannot be changed once the ElectionSession has begun.",
            },
            {
                "field_name": "start_time",
                "help_text": "Start time cannot be changed once the ElectionSession has begun.",
            },
            {
                "field_name": "upload_elections",
                "help_text": "Cannot bulk upload new Elections once the ElectionSession has begun.",
            },
            {
                "field_name": "upload_candidates",
                "help_text": "Cannot bulk upload new Candidates once the ElectionSession has begun.",
            },
            {
                "field_name": "upload_eligibilities",
                "help_text": "Cannot bulk upload new Eligibilities once the ElectionSession has begun.",
            },
        ]

        # Disable changing election start time, and bulk candidate & position uploads
        # once the election has begun.
        instance = getattr(
            self, "instance", None
        )  # Gets the ElectionSession instance currently being added/edited

        if (
            instance.start_time is not None
            and instance.start_time.astimezone(settings.TZ_INFO) < _now()
        ):
            for read_only_field in self.read_only_fields:
                self.fields[read_only_field["field_name"]].help_text = read_only_field[
                    "help_text"
                ]

    def clean(self):
        """
        Overrides the BaseForm clean() function. Adds functionality for ensuring the following:
        1. Certain fields aren't changed after an ElectionSession has started.
        2. Checks that there are either exactly 3 or exactly 0 CSV files uploaded. Otherwise errors out.
        3. If there are 3 CSV files uploaded we run checks on those 3 files and return, otherwise we just return.
        """
        cleaned_data = super().clean()

        if (
            self.cleaned_data["start_time"] is not None
            and self.cleaned_data["end_time"] is not None
            and self.cleaned_data["start_time"].astimezone(settings.TZ_INFO)
            >= self.cleaned_data["end_time"].astimezone(settings.TZ_INFO)
        ):
            raise forms.ValidationError(
                "The ElectionSession must start before it ends. Ensure that your start time is before your end time."
            )

        # Get a list of the field names that should be readonly
        read_only_field_names = [field["field_name"] for field in self.read_only_fields]
        illegally_changed_fields = list(
            set.intersection(set(self.changed_data), set(read_only_field_names))
        )

        # Ensure that fields aren't changed after election start
        if (
            self.instance.start_time is not None
            and self.instance.start_time.astimezone(settings.TZ_INFO) < _now()
            and illegally_changed_fields
        ):
            raise forms.ValidationError(
                f"{', '.join(field for field in sorted(illegally_changed_fields))} cannot be changed once "
                "the election session has begun. Revert changes, or leave and return to this page "
                "to reset all fields."
            )

        # Check the number of files uploaded
        raw_uploads = [
            self.cleaned_data["upload_elections"],
            self.cleaned_data["upload_candidates"],
            self.cleaned_data["upload_eligibilities"],
        ]

        # If 1 or 2 files were uploaded throw an error since all 3 files must be uploaded at once
        if 0 < raw_uploads.count(None) < 3:
            raise forms.ValidationError(
                "CSV Files for Elections, Candidates, and Eligibilities must all be uploaded all at once or "
                "none at all."
            )

        # If all files were uploaded extract the CSV data and pass it to the csv_checker functions
        elif raw_uploads.count(None) == 0:
            # Check to make sure user uploads a CSV and not a different type of file.
            for file in raw_uploads:
                if file.content_type != "text/csv":
                    raise forms.ValidationError(
                        "Ensure all uploaded files are CSV files. ODS, XLS and other spreadsheet extensions are not "
                        f"supported. Please upload your files again. Error at: [{file.name}]"
                    )

            # Make sure we're at the beginning of the file
            self.cleaned_data["upload_elections"].file.seek(0)
            elections_data = list(
                csv.reader(
                    io.StringIO(
                        self.cleaned_data["upload_elections"]
                        .file.read()
                        .decode("utf-8")
                    ),
                    delimiter=",",
                )
            )

            # Make sure we're at the beginning of the file
            self.cleaned_data["upload_candidates"].file.seek(0)
            candidates_data = list(
                csv.reader(
                    io.StringIO(
                        self.cleaned_data["upload_candidates"]
                        .file.read()
                        .decode("utf-8")
                    ),
                    delimiter=",",
                )
            )

            # Make sure we're at the beginning of the file
            self.cleaned_data["upload_eligibilities"].file.seek(0)
            eligibilities_data = list(
                csv.reader(
                    io.StringIO(
                        self.cleaned_data["upload_eligibilities"]
                        .file.read()
                        .decode("utf-8")
                    ),
                    delimiter=",",
                )
            )

            self.file_upload_list = {
                "elections": {
                    "header": elections_data.pop(0),
                    "body": elections_data,
                    "file_name": self.cleaned_data["upload_elections"].name,
                },
                "candidates": {
                    "header": candidates_data.pop(0),
                    "body": candidates_data,
                    "file_name": self.cleaned_data["upload_candidates"].name,
                },
                "eligibilities": {
                    "header": eligibilities_data.pop(0),
                    "body": eligibilities_data,
                    "file_name": self.cleaned_data["upload_eligibilities"].name,
                },
            }

            # Call the csv_checks
            self.csv_checks()
        return cleaned_data

    def csv_checks(self):
        """
        Main checks function. All other functions are called from here.
        This calls headers_check and lengths_check beforehand to ensure that the headers
        and number of entries per row are all standardized, since these parameters are used
        as references within the other checks functions.
        """

        # Insert check headers here before other checks
        self.headers_check()
        self.lengths_check()

        method_list = [
            method
            for method in dir(ElectionSessionAdminForm)
            if method.startswith("check_")
        ]
        for method in method_list:
            getattr(self, method)()

    def headers_check(self):
        """Checks if all the CSV files have the correct headers."""
        csv_files_to_check = ["elections", "candidates", "eligibilities"]
        for csv_file in csv_files_to_check:
            header_categories = []
            for category in self.file_upload_list[csv_file]["header"]:
                if category not in self.header_definitions[csv_file]:
                    ElectionSessionAdminForm.add_error(
                        self=self,
                        field=f"upload_{csv_file}",
                        error=f"[{self.file_upload_list[csv_file]['file_name']}] Invalid header. Header for the "
                        f"{csv_file.capitalize()} CSV must contain: {self.header_definitions[csv_file]}. "
                        f"Invalid header value found: [{category}]. Ensure there are no additional trailing commas "
                        f"at the end of the header.",
                    )
                    raise forms.ValidationError(
                        "Invalid header discovered. See more info below."
                    )
                header_categories.append(category)

            if set(self.header_definitions[csv_file]) != set(header_categories):
                ElectionSessionAdminForm.add_error(
                    self=self,
                    field=f"upload_{csv_file}",
                    error=f"[{self.file_upload_list[csv_file]['file_name']}] Invalid header. Header for "
                    f"{csv_file.capitalize()} CSV must contain: {self.header_definitions[csv_file]}. "
                    f" Categories missing: {set(self.header_definitions[csv_file]) - set(header_categories)}",
                )
                raise forms.ValidationError(
                    "Incomplete header discovered. See more info below."
                )

    def lengths_check(self):
        """
        Checks if all the rows in all the CSVs are the same length.
        Also checks that Elections and Eligibilities CSVs have the same number of rows.
        """

        error_found = False
        for key in self.file_upload_list:
            header = self.file_upload_list[key]["header"]
            body = self.file_upload_list[key]["body"]
            for row in body:
                if len(row) != len(header):
                    error_found = True
                    ElectionSessionAdminForm.add_error(
                        self=self,
                        field=f"upload_{key}",
                        error=f"[{self.file_upload_list[key]['file_name']}] All rows in the CSV must be the same "
                        f"length as the header. Ensure that any commas that may exist in text are enclosed in "
                        f"quotation marks. Ensure there are no additional trailing commas at the end of any"
                        f" rows.",
                    )
                    break
        if error_found:
            raise forms.ValidationError(
                "Invalid row length discovered. See more info below."
            )

        # Check that Election and Eligibility CSVs are the same length
        if len(self.file_upload_list["elections"]["body"]) != len(
            self.file_upload_list["eligibilities"]["body"]
        ):
            ElectionSessionAdminForm.add_error(
                self=self,
                field="upload_elections",
                error=f"[{self.file_upload_list['elections']['file_name']}] "
                f"Elections and Eligibilities CSVs must have the same number of rows. "
                f"Elections CSV has {len(self.file_upload_list['elections']['body'])} rows.",
            )
            ElectionSessionAdminForm.add_error(
                self=self,
                field="upload_eligibilities",
                error=f"[{self.file_upload_list['eligibilities']['file_name']}] "
                f"Elections and Eligibilities CSVs must have the same number of rows. "
                f"Eligibilities CSV has {len(self.file_upload_list['eligibilities']['body'])} rows.",
            )
            raise forms.ValidationError(
                "Election and Eligibilities don't match. See more info below."
            )

    def check_election_names(self):
        """
        Checks if the ElectionNames in Eligibilities and Candidates CSVs match the ones
        in the Elections CSV.
        """

        # Get a list of all election names
        elections_header = self.file_upload_list["elections"]["header"]
        elections_body = self.file_upload_list["elections"]["body"]
        election_name_index = elections_header.index("election_name")
        election_names_list = []
        for election_row in elections_body:
            election_names_list.append(election_row[election_name_index])

        # Check Candidates and Eligibilities CSVs
        csv_files_to_check = ["candidates", "eligibilities"]
        for csv_name in csv_files_to_check:
            header = self.file_upload_list[csv_name]["header"]
            body = self.file_upload_list[csv_name]["body"]
            election_name_index = header.index("election_name")
            for row in body:
                if row[election_name_index] not in election_names_list:
                    ElectionSessionAdminForm.add_error(
                        self=self,
                        field=f"upload_{csv_name}",
                        error=f"[{self.file_upload_list['elections']['file_name']}, "
                        f"{self.file_upload_list[csv_name]['file_name']}] "
                        f"Election names within the {csv_name.capitalize()} CSV must match those within the "
                        f"Elections CSV. Invalid Election name discovered: {row[election_name_index]}",
                    )
                    raise forms.ValidationError(
                        "Election names don't match over all CSV files."
                    )

    def check_election_seats_and_categories(self):
        """
        Checks that all the seats available are Integers and >=1.
        Checks that the Election Category is one of the Election.ELECTION_CATEGORY_CHOICES.
        """

        header = self.file_upload_list["elections"]["header"]
        body = self.file_upload_list["elections"]["body"]
        election_categories = [
            category[1] for category in Election.ELECTION_CATEGORY_CHOICES
        ]
        seats_index = header.index("seats_available")
        category_index = header.index("category")

        for row in body:
            if not row[seats_index].isnumeric():
                ElectionSessionAdminForm.add_error(
                    self=self,
                    field="upload_elections",
                    error=f"[{self.file_upload_list['elections']['file_name']}] seats_available for each election "
                    f"must be an integer.",
                )

            elif int(row[seats_index]) < 1:
                ElectionSessionAdminForm.add_error(
                    self=self,
                    field="upload_elections",
                    error=f"[{self.file_upload_list['elections']['file_name']}] seats_available for each election "
                    f"must be >=1.",
                )

            if row[category_index] not in election_categories:
                ElectionSessionAdminForm.add_error(
                    self=self,
                    field="upload_elections",
                    error=f"[{self.file_upload_list['elections']['file_name']}] Election category must be one of: "
                    f"[{', '.join(category for category in election_categories)}]. "
                    f"Incorrect election category found in CSV: [{row[category_index]}].",
                )

    def check_eligible_fields(self):
        """
        Checks that all the eligible fields are Integers and either 1 or 0 (T or F).
        Checks that status_eligible is one of the values in Eligibility.STATUS_CHOICES.
        """

        header = self.file_upload_list["eligibilities"]["header"]
        body = self.file_upload_list["eligibilities"]["body"]
        status_categories = [category[1] for category in Eligibility.STATUS_CHOICES]
        status_eligible_index = header.index("status_eligible")
        for row in body:
            if row[status_eligible_index] not in status_categories:
                ElectionSessionAdminForm.add_error(
                    self=self,
                    field="upload_eligibilities",
                    error=f"[{self.file_upload_list['eligibilities']['file_name']}] Eligibility status category must "
                    f"be one of: [{', '.join(category for category in status_categories)}]. "
                    f"Incorrect category found in CSV: [{row[status_eligible_index]}].",
                )
            for i in range(1, len(row) - 1):
                if not row[i].isnumeric() or (int(row[i]) not in [0, 1]):
                    ElectionSessionAdminForm.add_error(
                        self=self,
                        field="upload_eligibilities",
                        error=f"[{self.file_upload_list['eligibilities']['file_name']}] Eligibilities must be "
                        f"true/false values represented by the *integer* values of 1 or 0. "
                        f"Non-integer value found in CSV: [{row[i]}].",
                    )

    def save(self, commit=True):
        """
        Saves the ElectionSession and if CSV files were uploaded, creates and saves
        corresponding Elections, Candidates, and Eligibilities for that ElectionSession.

        Note: we save the Election Session before the rest of this function since we
        need the object to exist otherwise we get a ValueError in our parsing functions
        due to an unsaved related object.

        Note: We create the Elections first since Candidates will connect to an Election.
        Then create Eligibilities.

        Note:  ElectionSessions can be created without CSV files. When all three files are
        not uploaded then we only create the ElectionSession.
        """

        election_session = super().save(commit=commit)
        election_session.save()

        if (
            self.cleaned_data["upload_elections"] is not None
            and self.cleaned_data["upload_candidates"] is not None
            and self.cleaned_data["upload_eligibilities"] is not None
        ):
            self.save_all_csvs()

        return election_session

    def save_all_csvs(self):
        """
        Saves the CSV files for Elections, Candidates, and Eligibilities to the
        database, connected to the ElectionSession they were uploaded in.
        """

        self.csv_save_elections()
        self.csv_save_candidates()
        self.csv_save_eligibilities()

    def csv_save_elections(self):
        """
        Save the Elections from the elections.csv file.

        Note: if Elections already exist tied to that ElectionSession, it will delete
        all of them, as well as any Candidates and Eligibilities tied to that Election.
        It then remakes the Elections and ties in new Candidates and Eligibilities
        accordingly.
        """

        header = self.file_upload_list["elections"]["header"]
        body = self.file_upload_list["elections"]["body"]

        # Delete all entries for the ElectionSession being edited, if they exist
        old_elections = Election.objects.filter(election_session=self.instance)
        for election in old_elections:
            election.delete()

        # Create new entries
        for election_row in body:
            data = {
                "election_name": election_row[header.index("election_name")],
                "election_session": self.instance,
                "seats_available": election_row[header.index("seats_available")],
                "category": election_row[header.index("category")]
                .lower()
                .replace(" ", "_"),
            }
            election = Election(**data)
            election.save()

    def csv_save_candidates(self):
        """
        Save the Candidates from the candidates.csv file.
        """

        header = self.file_upload_list["candidates"]["header"]
        body = self.file_upload_list["candidates"]["body"]

        for candidate_row in body:
            election = Election.objects.filter(
                election_name=candidate_row[header.index("election_name")],
                election_session=self.instance,
            )[0]

            data = {
                "name": candidate_row[header.index("name")],
                "election": election,
                "statement": candidate_row[header.index("statement")],
            }
            candidate = Candidate(**data)
            candidate.save()

    def csv_save_eligibilities(self):
        """
        Save the Eligibilities from the eligibilities.csv file.
        """

        header = self.file_upload_list["eligibilities"]["header"]
        body = self.file_upload_list["eligibilities"]["body"]

        for eligibility_row in body:
            election = Election.objects.filter(
                election_name=eligibility_row[header.index("election_name")],
                election_session=self.instance,
            )[0]
            data = {
                "election": election,
                "eng_eligible": eligibility_row[header.index("eng_eligible")],
                "che_eligible": eligibility_row[header.index("che_eligible")],
                "civ_eligible": eligibility_row[header.index("civ_eligible")],
                "ele_eligible": eligibility_row[header.index("ele_eligible")],
                "cpe_eligible": eligibility_row[header.index("cpe_eligible")],
                "esc_eligible": eligibility_row[header.index("esc_eligible")],
                "ind_eligible": eligibility_row[header.index("ind_eligible")],
                "lme_eligible": eligibility_row[header.index("lme_eligible")],
                "mec_eligible": eligibility_row[header.index("mec_eligible")],
                "mms_eligible": eligibility_row[header.index("mms_eligible")],
                "year_1_eligible": eligibility_row[header.index("year_1_eligible")],
                "year_2_eligible": eligibility_row[header.index("year_2_eligible")],
                "year_3_eligible": eligibility_row[header.index("year_3_eligible")],
                "year_4_eligible": eligibility_row[header.index("year_4_eligible")],
                "pey_eligible": eligibility_row[header.index("pey_eligible")],
                "status_eligible": eligibility_row[header.index("status_eligible")]
                .lower()
                .replace(" ", "_"),
            }
            eligibility = Eligibility(**data)
            eligibility.save()
