from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import Group, PermissionsMixin
from django.core.mail import send_mail
from django.db.models import BooleanField, CASCADE, CharField, DateField, DateTimeField, EmailField, Model, OneToOneField, UUIDField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from common.permissions import generate_default_permissions


class UserManager(BaseUserManager):
    """
    Model manager for the surrogate user model.
    """

    def create_user(self, username, email, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Surrogate user model. Does not use password and has extra fields.
    Relies more on authentication backend to validate username etc.
    """

    subject_id = UUIDField("subject id", unique=True, db_index=True)
    username = CharField("username", unique=True, db_index=True, max_length=50)
    pretty_username = CharField("pretty username", unique=True, max_length=50, help_text="Same as the username, but allows different letter cases.")
    first_name = CharField("first name", max_length=50, blank=True)
    last_name = CharField("last name", max_length=50, blank=True)
    email = EmailField("email address", blank=True)
    is_staff = BooleanField("staff status", default=False, help_text="If the user can use the admin panel.")
    is_active = BooleanField("active status", default=False, help_text="If the user can log into the site.")
    date_joined = DateTimeField("date joined", default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        default_permissions = []
        permissions = [
            ("user.list", "List users"),
            ("user.view_basic", "View users' non-address info"),
            ("user.view_address", "View users' address"),
            ("user.delete", "Delete users"),
        ]
        permissions += generate_default_permissions("User", "users", actions=("view", "delete"))

    def clean(self):
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the combined full name.
        """
        full_name = "{0} {1}".format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class UserProfile(Model):
    user = OneToOneField(User, verbose_name="user", primary_key=True, related_name="profile", on_delete=CASCADE)
    birth_date = DateField("date of birth", null=True, blank=True)
    gender = CharField("gender", null=True, blank=True, max_length=50)
    country = CharField("country", null=True, blank=True, max_length=50)
    postal_code = CharField("postal code", null=True, blank=True, max_length=10)
    street_address = CharField("street address", null=True, blank=True, max_length=100)
    phone_number = CharField("phone number", null=True, blank=True, max_length=20)
    membership_years = CharField("membership years", null=True, blank=True, max_length=500,
                                 help_text="Comma separated list of years the user has been a member of the organization.")
    is_member = BooleanField("membership status", default=False, help_text="If the user is currently a member of the organization.")

    class Meta:
        default_permissions = []
        permissions = generate_default_permissions("UserProfile", "user profiles", actions=("view",))

    def __str__(self):
        return self.user.username

    def get_month(self):
        return "{0:02d}".format(self.birth_date.month)

    def get_day(self):
        return "{0:02d}".format(self.birth_date.day)

    def has_address(self):
        return self.street_address and self.postal_code


class GroupExtension(Model):
    group = OneToOneField(Group, verbose_name="group", primary_key=True, related_name="extension", on_delete=CASCADE)
    description = CharField("description", max_length=50, blank=True)
    is_superuser = BooleanField("superuser status", default=False, help_text="If users have every permission.")
    is_staff = BooleanField("staff status", default=False, help_text="If users can log into the admin panel.")
    is_active = BooleanField("active status", default=False, help_text="If users can log into the site.")

    class Meta:
        default_permissions = []
        permissions = [
            ("group.list", "List groups"),
            ("group.create", "Add groups"),
            ("group.change", "Change groups"),
            ("group.delete", "Delete groups"),
        ]
        permissions = generate_default_permissions("GroupExtension", "group extensions", actions=("view",))

    def __str__(self):
        return self.group.name


@receiver(post_save, sender=Group)
def group_save_listener(sender, instance, **kwargs):
    update_group_users(instance)


@receiver(post_save, sender=GroupExtension)
def group_extension_save_listener(sender, instance, **kwargs):
    update_group_users(instance.group)


def update_group_users(group):
    """Update all users in group to ensure consistency."""
    for user in group.user_set.all():
        is_superuser = False
        is_staff = False
        is_active = False
        for group in user.groups.all():
            group_ext = group.extension
            is_superuser = is_superuser or group_ext.is_superuser
            is_staff = is_staff or group_ext.is_staff
            is_active = is_active or group_ext.is_active
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.is_active = is_active
        user.save()
