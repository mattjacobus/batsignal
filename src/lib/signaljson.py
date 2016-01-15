import datetime
import decimal
import json

class SignalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return super(DecimalEncoder, self).default(o)

