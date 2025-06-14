from datetime import datetime

from graymatter.tools import Tool


class GetDate(Tool):
    def resolve(self):
        return f"Today's date is {datetime.today()}"
