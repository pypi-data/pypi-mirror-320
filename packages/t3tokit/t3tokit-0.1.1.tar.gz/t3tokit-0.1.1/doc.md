## use

### path
```
from libtokit.path import mkdirs

def test_create_directory():
    test_path = "./test_dir/sub_dir"
    
    # 调用函数创建目录
    err, msg = mkdirs(test_path)
    # 检查目录是否创建成功
    assert err == False, f"目录创建失败 err: {err}！{msg}"
    assert os.path.exists(test_path), "目录创建失败！"
    # 清理测试目录
    os.removedirs(test_path)

```
### oj call

```
from libtokit.call import Judger

def main():
    result = Judger.run(
        max_cpu_time=1000,
        max_real_time=3000,
        max_memory=128 * 1024 * 1024,
        max_stack=128 * 1024 * 1024,
        max_output_size=1024 * 1024,
        max_process_number=UNLIMITED,
        exe_path='/path/to/executable',
        input_path='/path/to/input',
        output_path='/path/to/output',
        error_path='/path/to/error',
        args=['arg1', 'arg2'],
        env=['ENV_VAR=value', 'ANOTHER_VAR=another_value'],
        log_path='/path/to/log',
        seccomp_rule_name='default',
        uid=1000,
        gid=1000,
        debug=True,
    )
    print(f'Result: {result}')
```


### oj parse

```
from libtokit.parse import parse_json, parse_yaml


def main():
    xml_file = 'test.xml'  # 替换为实际 XML 文件路径
    parser = ProblemParser(xml_file)  # 初始化解析器
    parser.parse()  # 解析 XML 文件
    parsed_data = parser.to_json()  # 转换为 JSON 格式
    if parsed_data:
        print(parsed_data)  # 打印 JSON 数据

```