import typer
import os
from neutools import debug


app = typer.Typer(no_args_is_help=True)


@app.command()
def start():
    """启动面板"""
    os.system("neu-start")


@app.command()
def stop():
    """停止面板"""
    os.system("neu-stop")


@app.command()
def restart():
    """重启面板"""
    os.system("neu-stop")
    os.system("neu-start")


@app.command()
def status():
    """查看面板状态"""
    os.system("neu-stat")


@app.command()
def install():
    """安装/升级/卸载面板"""
    os.system("bash -c \"$(wget -O - n.cxykevin.top)\"")


app.add_typer(debug.app, name="debug", help="调试工具")


if __name__ == "__main__":
    app()
