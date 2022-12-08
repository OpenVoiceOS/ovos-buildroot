from json.decoder import JSONDecodeError


class AuthenticationError(ValueError):
    """ unauthorized """


class SkillEntryError(ValueError):
    """ malformed skill entry """


class SkillRequirementsException(RuntimeError):
    """ Skill requirements installation failed """


class PipException(SkillRequirementsException):
    """ failed to run pip """


class GithubSkillEntryError(SkillEntryError):
    """ failed to understand github skill"""


class GithubInvalidUrl(GithubSkillEntryError):
    """ unrecognized url """


class GithubFileNotFound(FileNotFoundError, GithubInvalidUrl):
    """ unrecognized url """


class GithubInvalidBranch(GithubInvalidUrl):
    """ unrecognized branch """


class GithubRawUrlNotFound(GithubInvalidUrl):
    """ unrecognized raw url """


class GithubDownloadUrlNotFound(GithubInvalidUrl):
    """ unrecognized download url """


class GithubReadmeNotFound(GithubFileNotFound):
    """ could not extract readme from github """


class GithubLicenseNotFound(GithubFileNotFound):
    """ could not extract .desktop from github """


class InvalidManifest(GithubFileNotFound):
    """ manifest.yml from github is invalid YAML """


class GithubNotSkill(GithubInvalidUrl):
    """ does not seem to be an actual skill """


class UnknownAppstore(ValueError):
    """ unrecognized appstore """


class GithubAPIException(GithubInvalidUrl):
    """ an error occured with github api endpoints """


class GithubAPIInvalidBranch(GithubAPIException, GithubInvalidBranch):
    """ could not retrieve releases github api endpoints """


class GithubAPIReleasesNotFound(GithubAPIException):
    """ could not retrieve releases github api endpoints """


class GithubAPIFileNotFound(GithubFileNotFound, GithubAPIException):
    """ an error occured with github api endpoints """


class GithubAPIReadmeNotFound(GithubAPIFileNotFound, GithubReadmeNotFound):
    """ could not retrieve releases github api endpoints """


class GithubAPILicenseNotFound(GithubAPIFileNotFound, GithubLicenseNotFound):
    """ could not retrieve releases github api endpoints """


class GithubAPIRepoNotFound(GithubAPIException):
    """ could not retrieve releases github api endpoints """


class GithubAPIRateLimited(GithubAPIException):
    """ API rate limit exceeded """


class GithubHTTPRateLimited(GithubInvalidUrl):
    """ HTTP Abuse Detection rate limit"""
