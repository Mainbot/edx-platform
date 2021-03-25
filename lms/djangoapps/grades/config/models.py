"""
Models for configuration of the feature flags
controlling persistent grades.
"""


from config_models.models import ConfigurationModel
from django.conf import settings
from django.db.models import BooleanField, IntegerField, TextField
from django.utils.encoding import python_2_unicode_compatible

from openedx.core.lib.cache_utils import request_cached


@python_2_unicode_compatible
class PersistentGradesEnabledFlag(ConfigurationModel):
    """
    Enables persistent grades across the platform.
    When this feature flag is set to true, individual courses
    must also have persistent grades enabled for the
    feature to take effect.

    .. no_pii:

    .. toggle_name: PersistentGradesEnabledFlag.enabled
    .. toggle_implementation: ConfigurationModel
    .. toggle_default: False
    .. toggle_description: When enabled, grades are persisted. This means that PersistentCourseGrade objects are
       created for student grades. Alternatively, the PersistentGradesEnabledFlag.enabled_for_all_courses
       waffle flag or the PERSISTENT_GRADES_ENABLED_FOR_ALL_TESTS feature flag can be set to True to enable this
       feature for all courses.
    .. toggle_use_cases: temporary
    .. toggle_creation_date: 2016-08-26
    .. toggle_target_removal_date: None
    .. toggle_warnings: None
    .. toggle_tickets: https://github.com/edx/edx-platform/pull/13329
    """
    # this field overrides course-specific settings to enable the feature for all courses
    enabled_for_all_courses = BooleanField(default=True)

    @classmethod
    @request_cached()
    def feature_enabled(cls, course_id=None):
        """
        Looks at the currently active configuration model to determine whether
        the persistent grades feature is available.

        If the flag is not enabled, the feature is not available.
        If the flag is enabled and the provided course_id is for an course
            with persistent grades enabled, the feature is available.
        If the flag is enabled and no course ID is given,
            we return True since the global setting is enabled.
        """
        if settings.FEATURES.get('PERSISTENT_GRADES_ENABLED_FOR_ALL_TESTS'):
            return True
        if not PersistentGradesEnabledFlag.is_enabled():
            return False
        return True

    class Meta:
        app_label = "grades"

    def __str__(self):
        current_model = PersistentGradesEnabledFlag.current()
        return "PersistentGradesEnabledFlag: enabled {}".format(
            current_model.is_enabled()
        )


class ComputeGradesSetting(ConfigurationModel):
    """
    .. no_pii:
    """
    class Meta:
        app_label = "grades"

    batch_size = IntegerField(default=100)
    course_ids = TextField(
        blank=False,
        help_text="Whitespace-separated list of course keys for which to compute grades."
    )
