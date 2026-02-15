import multiprocessing as mp
import sys
import os
import time

def run_agent():
    """运行Agent服务"""
    import subprocess
    subprocess.run([sys.executable, "agent_service/agent_server.py"], cwd=os.path.dirname(os.path.abspath(__file__)))

def run_bot():
    """运行QQ机器人"""
    import subprocess
    subprocess.run([sys.executable, "bot/bot_client.py"], cwd=os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("启动多进程架构...")

    # 创建进程池，避免子进程继承锁
    mp.set_start_method('spawn', force=True)

    # 创建两个进程
    agent_process = mp.Process(target=run_agent)
    bot_process = mp.Process(target=run_bot)

    try:
        # 启动进程
        agent_process.start()
        time.sleep(1)  # 给agent一点启动时间
        bot_process.start()

        print("✅ Agent服务进程 PID:", agent_process.pid)
        print("✅ QQ机器人进程 PID:", bot_process.pid)
        print("所有服务已启动，按Ctrl+C退出")

        # 等待进程结束
        agent_process.join()
        bot_process.join()

    except KeyboardInterrupt:
        print("\n正在关闭服务...")
        agent_process.terminate()
        bot_process.terminate()
        agent_process.join()
        bot_process.join()
        print("服务已关闭")