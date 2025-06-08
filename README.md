# 个人财富管理系统

一个基于 Python 和 Streamlit 的个人财富管理应用，支持管理银行、港股、美股等资产。

## 功能特点

- 支持多种资产类型（银行、港股、美股）
- 自动获取实时汇率
- 资产统一以人民币（CNY）展示
- 资产趋势可视化
- 资产分布分析
- 数据本地存储

## 安装说明

1. 确保已安装 Python 3.10 或更高版本
2. 克隆项目到本地
3. 使用 uv 安装依赖：
   ```bash
   uv pip install -e .
   ```
4. 创建 `.env` 文件并配置汇率 API 密钥（可选）：
   ```
   EXCHANGE_RATE_API_KEY=your_api_key_here
   ```

## 运行应用

```bash
streamlit run app.py
```

## 项目结构

```
finance/
├── app.py                # 主程序入口
├── requirements.txt      # 依赖清单
├── pyproject.toml        # 项目配置
├── data/                 # 数据存储目录
├── modules/             # 功能模块
│   ├── asset_manager.py # 资产管理
│   ├── exchange.py      # 汇率管理
│   └── plotter.py       # 可视化
└── README.md            # 项目说明
```

## 开发说明

- 使用 `uv` 进行依赖管理
- 遵循 PEP 8 编码规范
- 使用 `black` 进行代码格式化
- 使用 `isort` 进行导入排序

## 许可证

MIT License
