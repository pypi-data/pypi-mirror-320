from ..ol_listener import OpenLineageListener


class OpenLineageResultListener(OpenLineageListener):
    def __init__(self, config=None, client=None):
        super().__init__(config=config, client=client)
