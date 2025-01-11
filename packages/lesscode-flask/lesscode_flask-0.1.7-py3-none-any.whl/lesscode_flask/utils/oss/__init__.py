import os
from io import BytesIO

from lesscode_flask.utils.helpers import app_config
from lesscode_flask.utils.oss.ks3_oss import Ks3Oss


class CommonOss:
    def __init__(self, storage_type, **kwargs):
        self.storage_type = storage_type
        self.storage_config = kwargs.get("storage_config", {}) if kwargs.get("storage_config", {}) else app_config.get(
            "STORAGE_CONFIG", {})

    def upload(self, **kwargs):
        file_url_list = []
        files = kwargs.get("files", [])
        if not files:
            raise Exception("files is empty")
        if self.storage_type == "ks3":
            storage_config = self.storage_config or dict()
            ks3 = Ks3Oss(**storage_config)
            for f in files:
                if not isinstance(f, dict):
                    file_name = f.filename
                    stream = f.stream.read()
                    file_stream = BytesIO(stream)
                    content = file_stream.getvalue().decode('utf-8')
                    url = ks3.save(key=file_name, content=content, content_type="string", policy="public-read")
                    file_url_list.append({"key": file_name, "url": url})
                else:
                    key = f.get("key", "")
                    _steam = f.get("stream")
                    stream = _steam.stream.read()
                    file_stream = BytesIO(stream)
                    content = file_stream.getvalue().decode('utf-8')
                    url = ks3.save(key=key, content=content, content_type="string", policy="public-read")
                    file_url_list.append({"key": key, "url": url})
        elif self.storage_type == "file":
            storage_dir = self.storage_config.get("storage_dir", "")
            if not storage_dir:
                storage_dir = app_config.get("STORAGE_DIR")
            if not storage_dir:
                raise Exception("storage_dir is empty")

            for f in files:
                if not isinstance(f, dict):
                    file_name = f.filename
                    stream = f.stream.read()
                    file_stream = BytesIO(stream)
                    file_path = os.path.join(storage_dir, file_name)
                    with open(file_path, 'wb') as outfile:
                        outfile.write(file_stream.getvalue())
                    file_url_list.append({"key": file_name, "url": file_path})
                else:
                    key = f.get("key", "")
                    _steam = f.get("stream")
                    stream = _steam.stream.read()
                    file_stream = BytesIO(stream)
                    key_list = []
                    if "\\" in key:
                        key_list = key.split("\\")
                    if "/" in key:
                        key_list = key.split("/")
                    file_path = storage_dir
                    if key_list:
                        for k in key_list:
                            file_path = os.path.join(file_path, k)
                    with open(file_path, 'wb') as outfile:
                        outfile.write(file_stream.getvalue())
                    file_url_list.append({"key": key, "url": file_path})
        return file_url_list

    def download(self, key):
        if self.storage_type == "ks3":
            storage_config = self.storage_config or dict()
            ks3 = Ks3Oss(**storage_config)
            return ks3.get_file(key)
        if self.storage_type == "file":
            storage_dir = self.storage_config.get("storage_dir", "")
            if not storage_dir:
                storage_dir = app_config.get("STORAGE_DIR")
            key_list = []
            if "\\" in key:
                key_list = key.split("\\")
            if "/" in key:
                key_list = key.split("/")
            file_path = storage_dir
            if key_list:
                for k in key_list:
                    file_path = os.path.join(file_path, k)
            with open(file_path, 'rb') as f:
                return f.read()
