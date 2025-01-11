from litechat import litechat_server
from litechat import litechat_codegpt_server,litechat_codegpt_legacy_server
from litechat import llamacpp_server

def run_server():
    litechat_server()

def run_server_animation():
    litechat_server(animation=True)

def codegpt_server():
    litechat_codegpt_server()

def codegpt_legacy_server():
    litechat_codegpt_legacy_server()

def run_llamacpp_server():
    llamacpp_server()
