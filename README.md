# IC Verification Toolbox | IC 验证工具箱

<div align="center">

A comprehensive toolkit for IC verification engineers built with Python and Tkinter.

一套为 IC 验证工程师打造的综合工具箱，基于 Python 和 Tkinter 构建。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

## Features | 功能特性

### 🛠️ Current Tools | 现有工具

1. **Base Converter | 进制转换器** (v1.1)
   - Convert between BIN/OCT/DEC/HEX formats
   - Support Verilog format, two's complement, variable bit width
   - Leading zero toggle, shift operations (logical/arithmetic)
   - 支持 BIN/OCT/DEC/HEX 互转，Verilog 格式、补码、多位宽、前导零、移位操作

2. **Data Slicer | 数据切片器**
   - Input HEX/BIN data and slice by 4/8/16/32/64/custom bits
   - Support Big/Little-Endian
   - Display in BIN/HEX/DEC(U)/DEC(S) formats
   - Click to copy individual cells
   - 输入 HEX/BIN 数据，按指定 bit 切片，支持大小端序，多格式显示，点击复制

3. **Data Diff | 数据比对器**
   - Two-way HEX/BIN input with bitwise comparison
   - Highlight differences in red
   - Summary table showing [hi:lo] positions of difference segments
   - Support left/right alignment and grouped display
   - 两路数据逐 bit 比对，差异位红色高亮，差异段汇总表，支持对齐和分组显示

4. **Bit Field Extractor | 位字段提取器**
   - Extract specified [hi:lo] bits from register values
   - Support HEX/BIN input
   - Visual display of original data and extraction results
   - 从寄存器值中提取指定位范围，支持 HEX/BIN 输入，可视化显示

### 🚀 Planned Tools | 计划中的工具

- Gray Code Converter | 格雷码转换器
- Byte Order Converter | 字节序转换器
- Waveform Analyzer | 波形分析
- Register Mapper | 寄存器映射
- CRC Calculator | CRC 计算
- SVA Assertion Template Generator | SVA 断言模板生成器

## Installation | 安装

### Prerequisites | 前置要求

- Python 3.8 or higher
- Tkinter (usually included with Python)

### Setup | 设置

```bash
# Clone the repository
git clone https://github.com/Clearluf/ic_toolbox.git
cd ic_toolbox

# Run the application
python -m ic_toolbox.main
```

Or directly run:

```bash
python ic_toolbox/main.py
```

## Usage | 使用方法

### Launch the Application | 启动应用

```bash
python ic_toolbox/main.py
```

### Navigation | 导航

- Use the sidebar on the left to switch between different tools
- 使用左侧侧边栏在不同工具间切换

### Example: Base Converter | 示例：进制转换器

1. Enter a value in any supported format
2. Select the desired output format
3. The results will be automatically displayed in all formats
4. 在任意支持的格式中输入值，选择所需的输出格式，结果将自动显示

## Architecture | 架构设计

```
ic_toolbox/
├── main.py              # Main entry point | 主入口
├── config.py            # Shared configuration (color theme, etc.) | 共享配置
├── sidebar.py           # Sidebar navigation | 侧边栏导航
└── tools/
    ├── __init__.py
    ├── base_converter.py    # Base converter tool | 进制转换器
    ├── data_slicer.py      # Data slicer tool | 数据切片器
    ├── data_diff.py        # Data diff tool | 数据比对器
    └── bit_extractor.py    # Bit field extractor | 位字段提取器
```

### Design Principles | 设计原则

- **Modular Architecture**: Each tool is an independent Frame class for easy extension
- **Centralized Configuration**: config.py manages theme colors and shared settings
- **Lazy Initialization**: Tools are created only when needed for better performance
- **模块化架构**：每个工具为独立的 Frame 类，便于扩展
- **集中配置**：config.py 集中管理主题颜色和共享设置
- **懒加载**：工具仅在需要时创建，提升性能

## UI Theme | UI 主题

The application uses the **Catppuccin Mocha** dark theme for a modern, eye-friendly interface.

应用采用 **Catppuccin Mocha** 深色主题，提供现代且护眼的界面。

## Contributing | 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献！请随时提交 Pull Request。

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License | 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## Author | 作者

**JingJ**

- GitHub: [Clearluf](https://github.com/Clearluf)

## Acknowledgments | 致谢

- Built with [Python](https://www.python.org/) and [Tkinter](https://docs.python.org/3/library/tkinter.html)
- UI Theme: [Catppuccin](https://catppuccin.com/)
- 基于 Python 和 Tkinter 构建，采用 Catppuccin 主题

---

<div align="center">

Made with ❤️ for IC Verification Engineers

为 IC 验证工程师打造

</div>
