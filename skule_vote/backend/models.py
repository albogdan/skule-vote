from django.db import models
from django.core import validators


DISCIPLINE_CHOICES = [
    ("ENG", "Track One Engineering"),
    ("CHE", "Chemical Engineering"),
    ("CIV", "Civil Engineering"),
    ("ELE", "Electrical Engineering"),
    ("CPE", "Computer Engineering"),
    ("ESC", "Engineering Science"),
    ("IND", "Industrial Engineering"),
    ("LME", "Mineral Engineering"),
    ("MEC", "Mechanical Engineering"),
    ("MMS", "Materials Science Engineering"),
]

STUDY_YEAR_CHOICES = [
    (1, "First Year"),
    (2, "Second Year"),
    (3, "Third Year"),
    (4, "Fourth Year"),
]


class ElectionSession(models.Model):
    class Meta:
        verbose_name_plural = "Election Sessions"

    election_session_name = models.CharField(
        max_length=50,
        null=False,
        help_text="Name your Election Session (i.e., Fall 2021).",
    )
    start_time = models.DateTimeField(
        null=False, help_text="When does your Election Session start?"
    )
    end_time = models.DateTimeField(
        null=False, help_text="When does your Election Session finish?"
    )

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return f"{self.election_session_name}"


class Election(models.Model):
    ELECTION_CATEGORY_CHOICES = [
        ("referenda", "Referenda"),
        ("officer", "Officer"),
        ("board_of_directors", "Board of Directors"),
        ("discipline_club", "Discipline Club"),
        ("class_representative", "Class Representative"),
        ("other", "Other"),
    ]

    election_name = models.CharField(
        max_length=80,
        null=False,
        help_text="Name your election (i.e., 4th Year Chair).",
    )
    election_session = models.ForeignKey(
        ElectionSession,
        related_name="elections",
        on_delete=models.CASCADE,
        null=False,
        help_text="Which Election Session does this election belong in?",
    )
    seats_available = models.IntegerField(
        null=False,
        validators=[
            validators.MinValueValidator(
                1, message="There must be at least one seat in each election."
            )
        ],
        help_text="How many seats are there in this election?",
    )

    category = models.CharField(
        max_length=50,
        choices=ELECTION_CATEGORY_CHOICES,
        null=False,
        help_text="What category does this election belong to?",
    )

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return f"{self.election_name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super(Election, self).save(force_insert, force_update, using, update_fields)

        data = {
            "name": "Reopen Nominations",
            "election": self,
            "statement": "Choose this option to reopen nominations.",
        }
        candidate = Candidate(**data)
        candidate.save()


class Candidate(models.Model):
    name = models.CharField(
        max_length=100,
        null=False,
        help_text="What is the name of the Candidate or Referendum?",
    )
    election = models.ForeignKey(
        Election,
        related_name="candidates",
        on_delete=models.CASCADE,
        null=False,
        help_text="Which Election is this Candidate/Referendum a part of?",
    )
    statement = models.TextField(
        null=True, blank=True, help_text="Enter Candidate or Referendum statement."
    )

    disqualified_status = models.BooleanField(
        null=False,
        default=False,
        help_text="Has the Candidate been disqualified? (Default is False). Ignore for Referenda.",
    )
    disqualified_link = models.URLField(
        null=True,
        help_text="(Optional) Enter a link to the disqualification ruling. Ignore for Referenda.",
        blank=True,
    )
    disqualified_message = models.TextField(
        null=True,
        help_text="(Optional) Enter a disqualification ruling message for this Candidate. Ignore for Referenda.",
        blank=True,
    )

    rule_violation_message = models.TextField(
        null=True,
        help_text="(Optional) Enter a rule violation message for this Candidate. Ignore for Referenda.",
        blank=True,
    )
    rule_violation_link = models.URLField(
        null=True,
        help_text="(Optional) Enter a link to the rule violation ruling. Ignore for Referenda.",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return f"{self.name}"


class Voter(models.Model):
    STATUS_CHOICES = [("full_time", "Full Time"), ("part_time", "Part Time")]

    student_number_hash = models.CharField(max_length=16, null=False)
    discipline = models.CharField(max_length=45, choices=DISCIPLINE_CHOICES, null=False)

    engineering_student = models.BooleanField(null=False)
    study_year = models.IntegerField(null=False, choices=STUDY_YEAR_CHOICES)
    pey = models.BooleanField(null=False)

    student_status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=False)

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return f"{self.student_number_hash}"


class Ballot(models.Model):
    voter = models.ForeignKey(
        Voter, related_name="ballots", null=False, on_delete=models.CASCADE
    )

    # Candidate and Rank will be null for a spoiled ballot
    candidate = models.ForeignKey(
        Candidate, related_name="ballots", null=True, on_delete=models.CASCADE
    )
    rank = models.IntegerField(null=True)

    election = models.ForeignKey(
        Election, related_name="ballots", null=False, on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self):
        return f"{self.voter} | {self.candidate}"


class Eligibility(models.Model):
    class Meta:
        verbose_name_plural = "Eligibilities"

    STATUS_CHOICES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("full_and_part_time", "Full and Part Time"),
    ]

    election = models.OneToOneField(
        Election,
        related_name="eligibilities",
        null=False,
        on_delete=models.CASCADE,
        help_text="Which election do you want to define eligibility for?",
    )

    eng_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Track One Engineering Eligible?"
    )
    che_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Chemical Engineering Eligible?"
    )
    civ_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Civil Engineering Eligible?"
    )
    ele_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Electrical Engineering Eligible?"
    )
    cpe_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Computer Engineering Eligible?"
    )
    esc_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Engineering Science Eligible?"
    )
    ind_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Industrial Engineering Eligible?"
    )
    lme_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Mineral Engineering Eligible?"
    )
    mec_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Mechanical Engineering Eligible?"
    )
    mms_eligible = models.BooleanField(
        null=False,
        default=False,
        verbose_name="Materials Science Engineering Eligible?",
    )

    year_1_eligible = models.BooleanField(
        null=False, default=False, verbose_name="First Years Eligible?"
    )
    year_2_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Second Years Eligible?"
    )
    year_3_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Third Years Eligible?"
    )
    year_4_eligible = models.BooleanField(
        null=False, default=False, verbose_name="Fourth Years Eligible?"
    )

    pey_eligible = models.BooleanField(
        null=False, default=False, verbose_name="PEY Students Eligible?"
    )
    status_eligible = models.CharField(
        max_length=30,
        null=False,
        choices=STATUS_CHOICES,
        help_text="Student statuses eligible",
    )

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return f"{self.election} Eligibility"


class Message(models.Model):
    message = models.TextField(
        null=False, help_text="This message will be displayed overhead the website."
    )
    election_session = models.ForeignKey(
        ElectionSession, related_name="messages", null=False, on_delete=models.CASCADE
    )

    active = models.BooleanField(
        null=False,
        default=True,
        help_text="Check to make alert active. Active alerts will appear on the website, inactive ones will not.",
    )
    hideable = models.BooleanField(
        null=False,
        default=False,
        help_text="Check to allow user to hide the alert on the website. Unchecked alerts will be persistent",
    )

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return f"{self.election_session} | {self.message[:15]}"
