DEFAULT_ASSISTANT_CR_NAME = "ark-assistant"
DEFAULT_REGION = "cn-beijing"


def get_default_cr_host() -> str:
    return f"{DEFAULT_ASSISTANT_CR_NAME}-{DEFAULT_REGION}.cr.volces.com"
