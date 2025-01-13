import os
from glob import glob
from pprint import pp

from pythonjsonlogger.json import JsonFormatter

bind = ["0.0.0.0:8000"]
forwarded_allow_ips = "*"
workers = 5

# Enable reloading
reload = os.getenv("PYQUOCCA_RELOAD", "").lower() not in ["", "false", "0", "f", "no"]
reload_extra_files = glob("./**/*.html", recursive=True)
if reload and os.getenv("PYQUOCCA_RELOAD_GLOBS", "") != "":
    globs = os.getenv("PYQUOCCA_RELOAD_GLOBS", "").split(",")
    for g in globs:
        reload_extra_files.extend(glob(g, recursive=True))


class GunicornJsonAccessLogger(JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(GunicornJsonAccessLogger, self).add_fields(
            log_record, record, message_dict
        )

        if isinstance(record.args, dict):
            for key, value in record.args.items():
                if (
                    key not in self.reserved_attrs
                    and not (hasattr(key, "startswith") and key.startswith("_"))
                    and key in self.rename_fields
                ):
                    log_record[self.rename_fields[key]] = value


def make_access_formatter():
    try:
        return GunicornJsonAccessLogger(
            fmt="%(M)s %(t)s %(r)s %(s)s %(p)s %(a)s %({host}i)s %({x-mtls-full-name}i)s %({x-forwarded-for}i)s %({x-mtls-username}i)s %({x-mtls-staff}i)s %({x-mtls-impersonated-by}i)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
            style="%",
            rename_fields={
                "M": "duration",
                "a": "user_agent",
                "t": "time",
                "{host}i": "host",
                "{x-forwarded-for}i": "ip",
                "s": "status",
                "r": "request",
                "p": "process_id",
                "{x-mtls-full-name}i": "full_name",
                "{x-mtls-username}i": "user",
                "{x-mtls-staff}i": "is_staff",
                "{x-mtls-impersonated-by}i": "impersonated_by",
            },
        )
    except Exception as e:
        pp(e)
        raise e


logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["console_access"],
            "qualname": "gunicorn.access",
        },
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["error_console"],
            "qualname": "gunicorn.error",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout",
        },
        "console_access": {
            "class": "logging.StreamHandler",
            "formatter": "json_access",
            "stream": "ext://sys.stdout",
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stderr",
        },
    },
    "formatters": {
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
        "json_access": {
            "()": "pyquocca.gunicorn.make_access_formatter",
        },
    },
}
