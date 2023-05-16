from .Extension import Extension
import os

ext_config: dict = {
    "name": "local_files",
    "arguments": {
        'action': 'str',
        'filename': 'str',
    },
    "description": "List files or send file in a local directory. (usage in response:/#local_files&list#/ or /#local_files&send&file.txt#/)",
    "refer_word": [],
    "max_call_times_per_msg": 1,
    "author": "白羽",
    "version": "0.0.1",
    "intro": "本地目录文件操作（真的是白羽写的）",
    "interrupt": True,
}

class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        custom_config: dict = self.get_custom_config()
        directory = arg_dict.get('directory', 'ng_local_files')

        if directory is None:
            return {
                'text': f"[Local Files] 未指定本地文件目录",
            }

        # 检测目录是否存在
        if not os.path.exists(directory):
            os.makedirs(directory)

        if arg_dict.get('action') == 'send':
            if arg_dict.get('filename') is None:
                return {
                    'text': f"[Local Files] 未指定文件名",
                    'notify': {
                        'sender': '[System]',
                        'msg': f"Send file failed, filename is None."
                    },
                    'wake_up': True,
                }
            return {
                'file': f"file:///{os.path.abspath(directory)}/{arg_dict.get('filename')}"
            }
        
        elif arg_dict.get('action') == 'list':
            try:
                file_list = os.listdir(directory)
                text = "\n".join(file_list)
            except Exception as e:
                return {
                    'notify': {
                        'sender': '[System]',
                        'msg': f"List files failed, error: {e}"
                    },
                    'wake_up': True,
                }

            return {
                'notify': {
                    'sender': '[System]',
                    'msg': f"List files in directory {directory} successfully.\n{text}"
                },
                'wake_up': True,
            }

        else:
            return {}

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)