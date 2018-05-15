from nhsorganisations.utils.version import get_version, get_stable_branch_name

# major.minor.patch.release.number
# release must be one of alpha, beta, rc, or final
VERSION = (0, 0, 0, 'alpha', 0)
__version__ = get_version(VERSION)
stable_branch_name = get_stable_branch_name(VERSION)

default_app_config = 'nhsorganisations.apps.NHSOrganisationsAppConfig'
