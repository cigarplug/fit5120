from datetime import datetime, tzinfo
from pytz import timezone, utc


melb = timezone("Australia/Melbourne")

utc_now = datetime.now(tz = utc)

fmt = "%Y-%m-%d %H:%M:%S"


def melb_now():
	return(utc_now.astimezone(melb).strftime(fmt))

