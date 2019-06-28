from django.utils.html import format_html
from django.contrib.staticfiles.templatetags.staticfiles import static

from wagtail.core import hooks


@hooks.register('insert_global_admin_css')
def add_wagtailadmin_widget_override_styles():
    # Add widget override styles for wagtailadmin
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static('nhsorganisations/widgets/organisationcheckboxselectmultiple/'
               'wagtailadmin.css')
    )
