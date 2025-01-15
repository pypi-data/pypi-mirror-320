# -*- coding: UTF-8 -*-
from pathlib import Path
from typing import Dict, Any, Literal

from omegaconf import OmegaConf as OC


class __Config:
    __DEFAULT_CONFIG__ = {
        'root': None,
        'mode': 'single',
        'generate': {
            'draft': False,
            'port': 4000
        },
        'default': {
            'editor': None,
            'draft': {
                'layout': 'post',
                'title': None,
                'categories': [],
                'tags': []
            },
            'post': {
                'layout': 'post',
                'title': None,
                'categories': [],
                'tags': [],
                'date': None
            }
        }
    }

    __DEPLOY_CONFIG__ = {
        'steps': [
            {'name': None, 'command': None},
            {'name': None, 'command': None},
        ]
    }


    def __init__(self):
        app_home = Path().home() / '.jekyll-cli'
        self.__root: Path | None = None
        self.__mode: str | None = None
        self.config_path = app_home / 'config.yml'

        # create app home
        app_home.mkdir(exist_ok=True)


    @property
    def root(self) -> Path | None:
        if self.__root is not None:
            return self.__root

        root: str | None = self.select('root')
        if not root:
            return None
        root: Path = Path(root)
        if not root.is_dir():
            raise None
        self.__root = root
        return self.__root


    @property
    def mode(self) -> str:
        if self.__mode is not None:
            return self.__mode

        mode: str = self.select('mode')
        self.__mode = mode
        return self.__mode


    def get_formatter(self, type_: str) -> Dict[str, Any]:
        formatter = self.select(f'default.{type_.lower()}', default={})
        return OC.to_container(formatter, resolve=True)


    def select(self, key: str, default=None, prefix: Literal['basic', 'deploy'] = 'basic') -> Any | None:
        config = self.__get_config(prefix)
        return OC.select(config, key, default=default) if config else None


    def update(self, key, value):
        config = self.__get_config()
        OC.update(config, key, value, merge=False)
        if key == 'root':
            self.__root = value
        elif key == 'mode':
            self.__mode = value
        OC.save(config, self.config_path)


    def reset(self):
        config = OC.create(self.__DEFAULT_CONFIG__)
        OC.save(config, self.config_path)


    def init(self, root, mode, generate_deploy):
        basic_config = self.__get_config()
        basic_config = OC.unsafe_merge(basic_config, {'root': root, 'mode': mode})
        OC.save(basic_config, self.config_path)

        if generate_deploy:
            deploy_path = self.root / 'jekyll-deploy.yml'
            deploy_config = OC.create(self.__DEPLOY_CONFIG__)
            OC.save(deploy_config, deploy_path)


    def to_dict(self) -> Dict[str, Any]:
        return OC.to_container(self.__get_config(), resolve=True)


    def __get_config(self, prefix: Literal['basic', 'deploy'] = 'basic') -> Dict[str, Any] | None:
        config = None
        if prefix == 'basic':
            if not self.config_path.exists():
                config = OC.create(self.__DEFAULT_CONFIG__)
                OC.save(config, self.config_path)
            else:
                config = OC.load(self.config_path)
        elif prefix == 'deploy':
            if self.root is not None:
                deploy_path = self.root / 'jekyll-deploy.yml'
                config = OC.load(deploy_path)
        return config


Config: __Config = __Config()
