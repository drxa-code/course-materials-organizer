# 课程资料整理工具

一个帮助学生把散落的学习资料按“课程／日期”整理到统一目录中的 Python 命令行工具。它会复制文件并保留源文件，支持先预览再执行。

## 项目状态

**最小可用版本已完成。** 当前已实现递归扫描、按课程和日期分类、文件名日期识别、同名文件防覆盖及预览模式；后续可继续增加图形界面和批量课程规则。

## 环境与获取

- 环境：Python 3.9 或更高版本。
- 依赖：仅使用 Python 标准库，无需安装第三方包。

```bash
git clone https://github.com/drxa-code/course-materials-organizer.git
cd course-materials-organizer
python3 organizer.py --help
```

Windows 环境可将命令中的 `python3` 换成 `python`。

## 最小使用示例

仓库自带两个用于体验的文本文件。先预览整理计划：

```bash
python3 organizer.py examples/inbox \
  --course "开源软件开发与实践" \
  --date 2026-10-31 \
  --output organized \
  --dry-run
```

确认输出无误后，去掉 `--dry-run` 执行：

```bash
python3 organizer.py examples/inbox \
  --course "开源软件开发与实践" \
  --date 2026-10-31 \
  --output organized
```

文件将被复制到：

```text
organized/
└── 开源软件开发与实践/
    └── 2026-10-31/
        ├── 第一讲-讲义.txt
        └── 第二讲-讲义.txt
```

整理自己的资料时，将 `examples/inbox` 替换为实际目录即可。省略 `--date` 时，工具优先识别文件名中的 `YYYY-MM-DD` 或 `YYYYMMDD`；无法识别时使用文件修改日期。目标位置存在同名文件时，会添加 `-1`、`-2` 等后缀，不覆盖原文件。

## 测试与核查

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖日期识别、课程目录名清理、复制整理、预览不写入、同名文件防覆盖，以及输出目录位于源目录内时避免重复扫描。

## 项目结构与依赖

```text
organizer.py              命令行入口与整理逻辑
tests/test_organizer.py   标准库 unittest 测试
examples/inbox/           可自行运行的小型示例
LICENSE                   MIT 许可证全文
compliance-analysis.md    开放目标、候选许可证比较与最终选择
CONTRIBUTING.md           问题反馈与代码贡献流程
```

当前版本未引入第三方代码、图片、字体、数据或文档，因此不需要 `THIRD_PARTY_NOTICES.md`。

## 如何贡献

- 反馈问题：在 [GitHub Issues](https://github.com/drxa-code/course-materials-organizer/issues) 中说明操作步骤、预期结果、实际结果和 Python 版本。
- 参与开发：阅读 [CONTRIBUTING.md](CONTRIBUTING.md)， fork 仓库后创建分支，提交包含测试的 Pull Request。
- 安全与隐私：不要上传账号密码、访问令牌、个人隐私或未经授权的课程资料。

## 许可证与选择理由

本项目采用 [MIT License](LICENSE)，适用于仓库中的原创代码和文档。MIT 允许使用、修改、分发和商用，也允许衍生作品以其他条款发布；其主要义务是在软件副本或重要部分中保留版权和许可声明。

本项目规模较小，目标是在保留作者信息的前提下降低学习者和开发者复用门槛，因此选择简洁、宽松的 MIT，而不强制衍生作品继续以相同许可证开源。候选许可证的详细比较见 [compliance-analysis.md](compliance-analysis.md)。
