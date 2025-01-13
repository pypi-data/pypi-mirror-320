import json

from aliyun.log import LogClient, LogItem, PutLogsRequest
from cobweb import setting


class LoghubDot:

    def __init__(self):
        self.client = LogClient(**setting.LOGHUB_CONFIG)

    def build(self, topic, **kwargs):

        temp = {}
        log_items = []
        log_item = LogItem()
        for key, value in kwargs.items():
            if not isinstance(value, str):
                temp[key] = json.dumps(value, ensure_ascii=False)
            else:
                temp[key] = value
        contents = sorted(temp.items())
        log_item.set_contents(contents)
        log_items.append(log_item)
        request = PutLogsRequest(
            project="databee-download-log",
            logstore="log",
            topic=topic,
            logitems=log_items,
            compress=True
        )
        self.client.put_logs(request=request)
