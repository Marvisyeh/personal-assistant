# LangChain Template

這是一個基於 LangChain 的專案模板，提供了快速開始使用 LangChain 框架的基礎結構。

## 功能特點

- 使用 FastAPI 作為 Web 框架
- 整合 LangChain 及其相關套件
- 支援多種 LLM 提供商（OpenAI、Anthropic 等）
- Docker 容器化支援
- 完整的開發環境配置

## 系統需求

- Python 3.12 或更高版本
- Docker 和 Docker Compose（可選，用於容器化部署）

## 快速開始

1. 克隆專案：

```bash
git clone <repository-url>
cd langchain-template
```

2. 安裝依賴：

```bash
pip install -e .
```

3. 運行應用：

```bash
python main.py
```

## 使用 Docker

1. 構建映像：

```bash
docker-compose build
```

2. 運行容器：

```bash
docker-compose up
```

## 專案結構

```
langchain-template/
├── app/            # 應用程式主要程式碼
├── docs/           # 專案文檔
├── logs/           # 日誌文件
├── main.py         # 應用程式入口點
├── pyproject.toml  # 專案配置和依賴
└── Dockerfile      # Docker 配置
```

## 依賴套件

- FastAPI >= 0.115.12
- LangChain >= 0.3.25
- LangChain-Anthropic >= 0.3.13
- LangChain-Community >= 0.3.24
- LangChain-OpenAI >= 0.3.17
- Uvicorn >= 0.34.2

## 開發指南

1. 確保您已經安裝了所有必要的依賴
2. 遵循專案的程式碼風格指南
3. 在提交代碼前運行測試
4. 使用提供的 Docker 配置進行本地開發

## 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件

## 貢獻

歡迎提交 Pull Requests 和 Issues！

## 支援

如有任何問題或需要協助，請開啟一個 Issue。
