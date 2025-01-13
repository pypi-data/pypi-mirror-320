# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['t3tokit']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 't3tokit',
    'version': '0.1.1',
    'description': 'A simple utility for creating directories.',
    'long_description': '## use\n\n### path\n```\nfrom libtokit.path import mkdirs\n\ndef test_create_directory():\n    test_path = "./test_dir/sub_dir"\n    \n    # 调用函数创建目录\n    err, msg = mkdirs(test_path)\n    # 检查目录是否创建成功\n    assert err == False, f"目录创建失败 err: {err}！{msg}"\n    assert os.path.exists(test_path), "目录创建失败！"\n    # 清理测试目录\n    os.removedirs(test_path)\n\n```\n### oj call\n\n```\nfrom libtokit.call import Judger\n\ndef main():\n    result = Judger.run(\n        max_cpu_time=1000,\n        max_real_time=3000,\n        max_memory=128 * 1024 * 1024,\n        max_stack=128 * 1024 * 1024,\n        max_output_size=1024 * 1024,\n        max_process_number=UNLIMITED,\n        exe_path=\'/path/to/executable\',\n        input_path=\'/path/to/input\',\n        output_path=\'/path/to/output\',\n        error_path=\'/path/to/error\',\n        args=[\'arg1\', \'arg2\'],\n        env=[\'ENV_VAR=value\', \'ANOTHER_VAR=another_value\'],\n        log_path=\'/path/to/log\',\n        seccomp_rule_name=\'default\',\n        uid=1000,\n        gid=1000,\n        debug=True,\n    )\n    print(f\'Result: {result}\')\n```\n\n\n### oj parse\n\n```\nfrom libtokit.parse import parse_json, parse_yaml\n\n\ndef main():\n    xml_file = \'test.xml\'  # 替换为实际 XML 文件路径\n    parser = ProblemParser(xml_file)  # 初始化解析器\n    parser.parse()  # 解析 XML 文件\n    parsed_data = parser.to_json()  # 转换为 JSON 格式\n    if parsed_data:\n        print(parsed_data)  # 打印 JSON 数据\n\n```',
    'author': 'pytools',
    'author_email': 'hyhlinux@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
