import os
import typer
from enum import Enum


class applicationTemplate():
    get_args = {
        "description": "描述",
        "version": "版本",
        "author": "作者",
        "license": "开源许可证协议",
        "url": "项目主页",
        "app_name": "应用名称"
    }

    def __init__(self, args):
        self.args = args

    def create_dirs(self):
        return [
            "ui",
            "static",
            "server",
            "static/css",
            "static/js",
            ".vscode"
        ]

    def create_files(self):
        return {
            f"static/css/{self.args['name']}.css": """body {
    margin: 0;
    padding: 0;
}
""",
            f"static/js/{self.args['name']}.js": f"""neutron.setTitle("{self.args['app_name']}")
neutron.setMinSize(500, 300)
neutron.getInfo((data) => {{
    if (data[0]["h"] < 300) {{
        neutron.setWinSize(500, 300)
    }}
}});
""",
            "ui/index.html": f"""<html lang="zh-cn">
<head>
    <meta charset="UTF-8">
    <title>{self.args['name']}</title>
    <script src="{{{{winapi}}}}"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{{{{static}}}}/css/{self.args['name']}.css">
    <script src="{{{{static}}}}/js/{self.args['name']}.js"></script>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>""",
            "icon.png": b'\x89PNG\r\n\x1a\n\x00\x00',
            "server/main.py": """from neutron import Plugin,execute

app = Plugin(__file__)

@app.route.get("/")
async def hello():
    return "Hello, World!"
""",
            "manifest.toml": f"""
[common]
name = "{self.args['name']}"
version = "{self.args['version']}"
description = "{self.args['description']}"
author = "{self.args['author']}"
license = "{self.args['license']}"
url = "{self.args['url']}"

[icon]
name = "{self.args['app_name']}"
image = "icon.png"

[window]
path = "ui"
static = "static"

[api]
path = "server/main.py"
object = "app"

""",
            ".vscode/settings.json": """{
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.extraPaths": [
        "/opt/neutron/neutron/server/api"
    ],
}"""
        }


class additionTemplate():
    get_args = {
        "description": "描述",
        "version": "版本",
        "author": "作者",
        "license": "开源许可证协议",
        "url": "项目主页"
    }

    def __init__(self, args):
        self.args = args

    def create_dirs(self):
        return [
            ".vscode"]

    def create_files(self):
        return {

            f"{self.args['name']}.js": "",
            f"{self.args['name']}.py": "",
            f"{self.args['name']}.css": "",
            "manifest.toml": f"""
[common]
name = "{self.args['name']}"
version = "{self.args['version']}"
description = "{self.args['description']}"
author = "{self.args['author']}"
license = "{self.args['license']}"
url = "{self.args['url']}"

[addition]
js = "{self.args['name']}.js"
css = "{self.args['name']}.css"
py = "{self.args['name']}.py"

""",
            ".vscode/settings.json": """{
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.extraPaths": [
        "/opt/neutron/neutron/server/api"
    ],
}"""
        }


class simpleTemplate():
    get_args = {
        "description": "描述",
        "version": "版本",
        "author": "作者",
        "license": "开源许可证协议",
        "url": "项目主页"
    }

    def __init__(self, args):
        self.args = args

    def create_dirs(self):
        return []

    def create_files(self):
        return {
            "manifest.toml": f"""
[common]
name = "{self.args['name']}"
version = "{self.args['version']}"
description = "{self.args['description']}"
author = "{self.args['author']}"
license = "{self.args['license']}"
url = "{self.args['url']}"
"""
        }


class templateTypeEnum(str, Enum):
    application = "application"
    addition = "addition"
    simple = "simple"


template_list = {
    "application": applicationTemplate,
    "addition": additionTemplate,
    "simple": simpleTemplate
}


neu_path = os.environ.get("NEU_PATH")
if neu_path is None:
    neu_path = "/opt/neutron/neutron"


app = typer.Typer(no_args_is_help=True)


@app.command()
def create(name: str, path: str = ".", template: templateTypeEnum = templateTypeEnum.application):
    """从模板创建"""
    template_use = template_list[template.value]
    args_res = {}
    args_res["name"] = name
    typer.echo(f"\033[34m使用模板\033[0m: {template.value}")
    for k, v in template_use.get_args.items():
        args_res[k] = typer.prompt("\033[34m"+v+"\033[0m", prompt_suffix=": ")
    template_c = template_use(args_res)
    os.makedirs(path+os.sep+name, exist_ok=True)
    for i in template_c.create_dirs():
        os.makedirs(path+os.sep+name+os.sep+i, exist_ok=True)
    typer.echo("\033[32m创建中\033[0m...")
    for k, v in template_c.create_files().items():
        if (type(v) == str):
            with open(path+os.sep+name+os.sep+k, "w") as f:
                f.write(v)
        else:
            with open(path+os.sep+name+os.sep+k, "wb") as f:
                f.write(v)
    typer.echo("\033[32m创建完成！\033[0m")


@app.command()
def run(path: str = ".", port=1231):
    if (not os.path.exists(neu_path)):
        raise ModuleNotFoundError(
            "Cannot Find neutron panel!\nYou can use \"NEU_PATH\" to set the path.")
    """运行"""
    if (not os.path.exists(path+os.sep+"manifest.toml")):
        raise FileNotFoundError(
            "manifest.toml is missing, maybe it is not a valid plugin.")
    abs_path = os.path.abspath(path)
    print(
        f"cd /opt/neutron/neutron && source /opt/neutron/neutron/venv/bin/activate && sudo python main.py --set-config:server.port={port} --set-config:debug.debug=True --add-config:plugin.load_single_plugins={abs_path}")
    os.system(
        f"cd /opt/neutron/neutron && source /opt/neutron/neutron/venv/bin/activate && sudo python main.py --set-config:server.port={port} --set-config:debug.debug=True --add-config:plugin.load_single_plugins={abs_path}")
