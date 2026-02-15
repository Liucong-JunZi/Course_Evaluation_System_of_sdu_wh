# 异步分离架构QQ机器人

## 架构
两个独立进程，TCP通信：
- Agent服务 (8765端口)
- QQ机器人

## 启动
```bash
python main_multi_process.py
```

## 目录
```
├── shared/               # 共享消息类型
├── agent_service/        # AI服务
├── bot/                  # QQ机器人
├── config.yaml
└── main_multi_process.py # 多进程启动
```