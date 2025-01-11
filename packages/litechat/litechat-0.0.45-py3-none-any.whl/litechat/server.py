from ._llama_cpp._oai_api import llamacpp_server
from ._core._api import litechat_server


def server(
    models_dir: str = None,
    host="0.0.0.0",
    port=11437,
    log_level="info",
    animation=False,
    **model_kwargs
):
    if models_dir:
        llamacpp_server(models_dir, host, port, **model_kwargs)
    else:
        litechat_server(host, port, log_level, animation)
