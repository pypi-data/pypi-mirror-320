# -*- coding: utf-8 -*-
import socket
import sys
import inquirer

from autowork_cli.common.config.PublicConfig import (PRODUCT_LIST, OTHER, OTHER_NAME, APP_REQUEST, PRODUCT_MAP,
                                                     PRODUCT_NAME_MAP)
from autowork_cli.common.request.CybotronSyncClient import CybotronSyncClient
from autowork_cli.common.config.BaseURLConfig import get_url_config
from autowork_cli.common.config.LoginConfig import LoginConfig
from rich import print
from autowork_cli.util.apikeyutil import ApiKeyUtil


class LoginCommand:
    def __init__(self):
        self.config = LoginConfig()

    def run_login(self):
        # 初始化函数
        print("登录 Autowork...")

        self.ask_product()
        self.ask_env()
        self.ask_api_key()
        self.ask_tenant()
        self.ask_dev_apps()
        self.ask_computer_name()

        self.hello()

    def ask_product(self):
        answer = inquirer.prompt([
            inquirer.List(
                "product",
                message="选择要登录的产品?",
                choices=PRODUCT_LIST,
                default=PRODUCT_NAME_MAP[self.config.get_product()] if self.config.get_product() else ""
            )
        ])
        product_name = PRODUCT_MAP[answer["product"]]
        self.config.set_product(product_name)
        self.config.save()
        return product_name

    def ask_env_url(self):
        answer = inquirer.prompt([
            inquirer.Text('env_url',
                          message="请输入环境域名"
                          )
        ])

        env_url = answer['env_url'].strip()
        if not env_url.startswith("http"):
            env_url = "https://" + env_url
        print(env_url)
        self.config.set_env(OTHER)
        self.config.set_other_url(env_url)
        self.config.save()

    def ask_env(self):
        # tuple (label, value) list
        url_config = get_url_config(self.config.get_product())
        choices_list = [(a + ": " + url_config.get_domain_url(a), a) for a in url_config.get_env_list()]
        choices_list.append(("其他", "其他"))
        answer = inquirer.prompt([
            inquirer.List(
                "env",
                message="选择要登录的环境?",
                choices=choices_list,
                default="其他" if self.config.get_env() == "OTHER" else self.config.get_env()
            )
        ])
        if answer['env'] == OTHER_NAME:
            self.ask_env_url()
            return
        self.config.set_env(answer["env"])
        self.config.save()

    def ask_api_key(self):
        safe_apikey = ApiKeyUtil.safe_display(self.config.get_api_key())
        answer = inquirer.prompt([
            inquirer.Text('api_key',
                          message="请输入您的API KEY",
                          default=safe_apikey),
        ])

        if safe_apikey != answer["api_key"]:
            self.config.set_api_key(answer["api_key"])
            self.config.save()

    def ask_tenant(self):
        client = CybotronSyncClient()
        try:
            tenants_info = client.get("cbn/api/v1/tenant/user/tenants").get("result")
            tenant_code_list = [(f'{tenant["code"]}({tenant["name"]})', tenant['id']) for tenant in tenants_info]
            tenant_code_dict = dict(tenant_code_list)
            if len(tenants_info) == 1:
                tenant_code = tenant_code_list[0][0]
                answer = inquirer.prompt([
                    inquirer.Text('tenant', message=f"现在登录的是{tenant_code}租户", default=tenant_code)])
            else:
                tenant_code_list = [tenant[0] for tenant in tenant_code_list]
                answer = inquirer.prompt([
                    inquirer.List("tenant", message="选择要登录的租户?", choices=tenant_code_list, default=tenant_code_list[0])])
            self.config.set_tenant_id(tenant_code_dict[answer["tenant"]])
            self.config.save()
        except Exception as e:
            print(e)
            print(f"[red]登录失败：无法连接到 {self.config.get_env()} 环境，请检查密钥、网络或联系管理员")
            sys.exit(1)  # 退出登录流程

    def ask_dev_apps(self):
        while True:
            answer = inquirer.prompt([
                inquirer.Text('dev_apps',
                              message="请输入一个您正要开发的应用编码，多个应用请用','隔开",
                              default=self.config.get_dev_apps()),
            ])
            if not answer["dev_apps"]:
                print("[red]开发的应用编码不能为空")
            elif not verify_app(answer["dev_apps"].split(',')):
                print("[red]当前租户下未找到输入的应用，请检查输入是否正确")
                continue
            else:
                break
        self.config.set_dev_apps(answer["dev_apps"])
        self.config.save()

    def ask_computer_name(self):
        while True:
            answer = inquirer.prompt([
                inquirer.Text('computer_name',
                              message="请输入您计算机名称",
                              default=socket.gethostname(),),
            ])
            if not answer["computer_name"]:
                print("[red]计算机名称不能为空")
            else:
                break
        self.config.set_computer_name(answer["computer_name"])
        self.config.save()

    def hello(self):
        client = CybotronSyncClient()
        try:
            userinfo = client.get("usr/api/v1/getUserInfo").get("result")
            username = userinfo.get('name')
            print(f"[green]你好, {username}, Autowork {self.config.get_env()}环境连接成功！")
        except Exception as _:
            print(f"[red]连接失败: 请确认API KEY是否正确，或者确认连接的赛博坦环境是否启动")


def verify_app(input_app: list):
    try:
        client = CybotronSyncClient()
        app_list = client.post("cbn/api/v1/tenant/app/getList", json=APP_REQUEST).get("result").get("data")
    except Exception as _:
        print(f"[red], 请检查网络或联系管理员")
        sys.exit(1)  # 退出登录流程
    app_list = [app_id['app_id'] for app_id in app_list]
    for app_id in input_app:
        if app_id in app_list:
            continue
        else:
            return False
    return True
