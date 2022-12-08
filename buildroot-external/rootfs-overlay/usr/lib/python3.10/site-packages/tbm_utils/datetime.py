__all__ = [
	'DATETIME_RE',
	'ParsedDateTime',
	'datetime_string_to_time_period'
]

import re

import pendulum
from attr import attrib, attrs
from pendulum import DateTime
from pendulum.tz import fixed_timezone


DATETIME_RE = re.compile(
	# Date (optional)
	r"^"
	r"(?:"
	r"	(?P<year>\d{4})"
	r"	[-\s]?"
	r"	(?P<month>\d{2})?"
	r"	[-\s]?"
	r"	(?P<day>\d{1,2})?"
	r")"
	# Time (optional)
	r"(?:"
	r"	[T\s]"
	r"	(?P<hour>\d{1,2})"
	r"	:?"
	r"	(?P<minute>\d{1,2})?"
	r"	:?"
	r"	(?P<second>\d{1,2})?"
	# Timezone offset (optional)
	r"	(?:"
	r"		(?P<tz_oper>[-+\s])"
	r"		(?P<tz_hour>\d{1,2})"
	r"		:?"
	r"		(?P<tz_minute>\d{1,2})?"
	r"	)?"
	r")?"
	r"$",
	re.VERBOSE
)


def _convert_to_int(value):
	if value is not None:
		value = int(value)

	return value


@attrs(slots=True, frozen=True, kw_only=True)  # pragma: nocover
class ParsedDateTime:
	year = attrib(converter=_convert_to_int)
	month = attrib(converter=_convert_to_int)
	day = attrib(converter=_convert_to_int)
	hour = attrib(converter=_convert_to_int)
	minute = attrib(converter=_convert_to_int)
	second = attrib(converter=_convert_to_int)
	tz_oper = attrib()
	tz_hour = attrib(converter=_convert_to_int)
	tz_minute = attrib(converter=_convert_to_int)


def datetime_string_to_time_period(
	dt_string,
	*,
	in_=False,
	on=False,
	before=False,
	after=False
):
	if not any([in_, on, before, after]):
		raise ValueError("One of in_, on, before, or after must be ``True``.")

	if dt_string == 'today':
		dt_string = pendulum.today().to_date_string()
	elif dt_string == 'yesterday':
		dt_string = pendulum.yesterday().to_date_string()
	elif dt_string == 'now':  # pragma: nocover
		dt_string = pendulum.now().end_of('minute').to_datetime_string()

	match = DATETIME_RE.match(dt_string)

	if (
		not match
		or match['year'] is None
	):
		raise ValueError(
			f"'{dt_string}' is not a supported datetime string."
		)

	parsed = ParsedDateTime(**match.groupdict())

	if parsed.tz_hour:
		tz_offset = 0
		if parsed.tz_hour is not None:  # pragma: nobranch
			tz_offset += parsed.tz_hour * 3600
		if parsed.tz_minute is not None:  # pragma: nobranch
			tz_offset += parsed.tz_minute * 60
		if parsed.tz_oper == '-':  # pragma: nobranch
			tz_offset *= -1
		parsed_tz = fixed_timezone(tz_offset)
	else:
		parsed_tz = pendulum.local_timezone()

	if in_:
		if parsed.day:
			raise ValueError(
				f"Datetime string must contain only year or year/month for 'in' option."
			)
		start = pendulum.datetime(
			parsed.year,
			parsed.month or 1,
			parsed.day or 1,
			tz=parsed_tz
		)

		if parsed.month:
			end = start.end_of('month')
		else:
			end = start.end_of('year')

		period = pendulum.period(start, end)
	elif on:
		if (
			not all(
				getattr(parsed, attr)
				for attr in ['year', 'month', 'day']
			)
			or parsed.hour
		):
			raise ValueError(
				f"Datetime string must contain only year, month, and day for 'on' option."
			)

		dt = pendulum.datetime(
			parsed.year,
			parsed.month,
			parsed.day,
			tz=parsed_tz
		)

		period = pendulum.period(dt.start_of('day'), dt.end_of('day'))
	elif before:
		start = DateTime.min

		dt = pendulum.datetime(
			parsed.year,
			parsed.month if parsed.month is not None else 1,
			parsed.day if parsed.day is not None else 1,
			parsed.hour if parsed.hour is not None else 23,
			parsed.minute if parsed.minute is not None else 59,
			parsed.second if parsed.second is not None else 59,
			0,
			tz=parsed_tz
		)

		if parsed.month is None:
			dt = dt.start_of('year')
		elif parsed.day is None:
			dt = dt.start_of('month')
		elif parsed.hour is None:
			dt = dt.start_of('day')
		elif parsed.minute is None:
			dt = dt.start_of('hour')
		elif parsed.second is None:
			dt = dt.start_of('minute')

		period = pendulum.period(start, dt)
	else:
		end = DateTime.max

		dt = pendulum.datetime(
			parsed.year,
			parsed.month if parsed.month is not None else 1,
			parsed.day if parsed.day is not None else 1,
			parsed.hour if parsed.hour is not None else 23,
			parsed.minute if parsed.minute is not None else 59,
			parsed.second if parsed.second is not None else 59,
			0,
			tz=parsed_tz
		)

		if parsed.month is None:
			dt = dt.end_of('year')
		elif parsed.day is None:
			dt = dt.end_of('month')
		elif parsed.hour is None:
			dt = dt.end_of('day')
		elif parsed.minute is None:
			dt = dt.start_of('hour')
		elif parsed.second is None:
			dt = dt.start_of('minute')

		period = pendulum.period(dt, end)

	return period
