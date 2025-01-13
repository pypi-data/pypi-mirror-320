## StoryBuilder

StoryBuilder 是一个用于构建和管理多语言故事内容的 Python 包。

## 安装

```
pip install storybuilder
```

## 项目结构

```
src/storybuilder/
├── core/           # 核心功能模块
│   ├── mtext.py   # 多语言文本处理
│   ├── mlist.py   # 多语言列表处理
│   └── mhtml.py   # 多语言HTML处理
├── models/         # 数据模型
│   ├── content.py # 内容模型
│   ├── board.py   # 画板模型
│   ├── script.py  # 脚本模型
│   ├── event.py   # 事件模型
│   └── actor.py   # 角色模型
├── builders/       # 构建器
│   ├── story_builder.py  # 故事构建器
│   └── voice_builder.py  # 语音构建器
├── utils/          # 工具类
│   ├── constants.py # 常量定义
│   └── helpers.py   # 辅助函数
└── services/       # 外部服务
    └── cos_uploader.py # COS上传服务
```

## 使用示例

### 基本使用

```python
from storybuilder import MText, Content, StoryBuilder

# 创建多语言文本
text = MText({
    "zh-CN": "你好，世界",
    "en-US": "Hello, World"
})

# 创建内容
content = Content(
    text=text,
    type="text"
)

# 使用故事构建器
builder = StoryBuilder()
builder.add_content(content)
```

### 多语言列表处理

```python
from storybuilder import MList

# 创建多语言列表
items = MList({
    "zh-CN": ["项目1", "项目2"],
    "en-US": ["Item 1", "Item 2"]
})

# 获取指定语言的列表
zh_items = items.get_list("zh-CN")  # ["项目1", "项目2"]
```

### HTML内容处理

```python
from storybuilder import MHTML

# 创建HTML内容
html = MHTML("<div>{content}</div>")
html.addElement("content", "Hello World")
result = html.export()  # "<div>Hello World</div>"
```

### 文件上传

```python
from storybuilder import CosUploader

# 初始化上传服务
uploader = CosUploader("config.json")

# 上传文件
success = uploader.upload_file("local.txt", "remote/path.txt")
```

## 配置

### COS配置示例 (config.json)

```json
{
    "region": "your-region",
    "secret_id": "your-secret-id",
    "secret_key": "your-secret-key",
    "bucket": "your-bucket"
}
```

## 开发

### 运行测试

```bash
python -m pytest test/
```

### 目录说明

- `core/`: 核心功能模块，包含基础的多语言文本和列表处理
- `models/`: 数据模型模块，包含业务相关的数据结构
- `builders/`: 构建器模块，提供故事和语音构建功能
- `utils/`: 工具模块，包含常量定义和辅助函数
- `services/`: 服务模块，提供外部服务集成

## 版本历史

### 1.0.0
- 重构项目结构，优化模块组织
- 改进多语言支持
- 增强错误处理
- 完善文档和测试

## 许可证

MIT License
