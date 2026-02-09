# NekoAgent Demo

## 必要前置
- 由于本项目是基于 ollama 本地搭建的 agent，所以首先请确保已安装 ollama
> [ollama下载地址](https://ollama.ai/)

- 有了 ollama 后，请按照以下步骤进行操作：
    - 启动 ollama 并保持后台运行
    - 下载模型并测试模型可用
    - 修改 `config.yaml` 中的 `models ` 为你下载的模型，务必保证模型名称正确，如果不知道模型名称，可以终端运行
    
    ```bash
    ollama list
    ```
    
- 接着需要安装所需要的库，请确保 `python >= 3.13`

```python
pip install -r requirements.txt
```

## 食用方式

终端运行

```python
streamlit run web.py
```

打开web界面，注意该web页面处于未完工状态，不支持 `PostgresHistory` 数据库记忆存储

或者直接运行 `agent.py` 使用终端对话

