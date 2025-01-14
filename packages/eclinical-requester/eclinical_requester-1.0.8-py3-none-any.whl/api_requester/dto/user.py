# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 03/18/2024 3:48 PM
@Description: Description
@File: authorize.py
"""


class EClinicalUser:

    def __init__(self, username=None, password=None, sponsor=None, study=None, test_env=None, app_env=None, app=None,
                 company=None, role=None, external=False):
        # username 用户名
        # password 密码
        # app 访问的系统
        # sponsor 访问sponsor 如果不需要，则传None
        # study 访问sponsor 如果不需要，则传None
        # test_env 访问的服务器环境
        self.username = username
        self.password = password
        self.app = app
        self.sponsor = sponsor
        self.study = study
        self.app_env = app_env
        self.test_env = str(test_env)
        self.company = company
        self.role = role
        self.external = external
        self.company_level_login = False

    def __repr__(self):
        attributes = self.__dict__
        info = list()
        for item in ["test_env", "username", "role", "company", "sponsor", "study"]:
            if attributes.get(item) is not None:
                info.append(str(attributes.get(item)))
        return "/".join(info)
