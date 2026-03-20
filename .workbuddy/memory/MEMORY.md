# Long-term Memory

## 用户信息
- 职业：IC验证工程师
- 技术偏好：Python，熟悉 Verilog/SystemVerilog

## 项目：IC验证工具箱
- 路径：`c:/Users/jingj/WorkBuddy/20260321000740/ic_toolbox/`
- 技术栈：Python + tkinter
- UI风格：Catppuccin Mocha 深色主题

### 目录结构（重构后）
```
ic_toolbox/
├── main.py           # 主入口
├── config.py         # 共享配置（颜色主题等）
├── sidebar.py        # 侧边栏导航
└── tools/
    ├── __init__.py
    ├── base_converter.py   # 进制转换器
    ├── data_slicer.py     # 数据切片器
    └── data_diff.py       # 数据比对器
```

### 架构
- 侧边导航 + 内容区，每个工具为独立 Frame 类
- config.py 集中管理主题颜色
- tools/ 目录下各工具独立模块，便于扩展

### 已有工具
1. 进制转换器（完成 v1.1）- BIN/OCT/DEC/HEX，支持Verilog格式、补码、多位宽、前导零开关、移位操作（逻辑/算术）
2. 数据切片器（完成）- 输入HEX/BIN数据，按4/8/16/32/64/自定义bit切片，支持Big/Little-Endian，显示BIN/HEX/DEC(U)/DEC(S)，可点击复制单格
3. 数据比对器（完成）- 两路HEX/BIN输入，逐bit比较，差异位红色高亮，差异段汇总表显示[hi:lo]位置，支持左/右对齐、分组显示
4. 位字段提取器（完成）- 从寄存器值中提取指定 [hi:lo] 位，支持 HEX/BIN 输入，可视化显示原始数据和提取结果

### 计划中的工具
- 格雷码转换器
- 字节序转换器
- 波形分析
- 寄存器映射
- CRC计算
- SVA断言模板
