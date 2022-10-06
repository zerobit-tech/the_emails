import logging
import logging.config  # needed when logging_config doesn't start with logging.config
from django.conf import settings

class EmailGroupFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        record.email_group_name= ""
        if message.startswith('@'):
            group_name = (message.split(":")[0])[1:]

            if group_name:
                record.email_group_name=  group_name.strip()
                return True 

        return False

