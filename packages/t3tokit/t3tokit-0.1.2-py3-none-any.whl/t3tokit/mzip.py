import os
import shutil
import pyminizip


def compress_directory_with_password(directory_path, zip_path, password):
    # 先使用 shutil 压缩整个目录，不带密码
    temp_zip = "temp.zip"
    shutil.make_archive(temp_zip.replace('.zip', ''), 'zip', directory_path)

    # 使用 pyminizip 对生成的 ZIP 文件加密
    pyminizip.compress(temp_zip, None, zip_path, password, 5)

    # 删除临时文件
    os.remove(temp_zip)
    return