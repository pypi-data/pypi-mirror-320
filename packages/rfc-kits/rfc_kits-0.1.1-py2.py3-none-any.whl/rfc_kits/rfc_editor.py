# coding:utf-8

import os
from typing import Optional
from urllib.parse import urljoin

from requests.exceptions import HTTPError
from sitepages import page


class rfc_page(page):
    BASE: str = "https://www.rfc-editor.org"

    def __init__(self, location: str, filepath: Optional[str] = None):
        super().__init__(urljoin(self.BASE, location))
        self.__filepath: str = filepath or location

    @property
    def filepath(self) -> str:
        return self.__filepath

    def save(self):
        rewrite: bool = not os.path.isfile(self.filepath)
        dirname: str = os.path.dirname(self.filepath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        try:
            datas: bytes = super().fetch().content
        except HTTPError:
            return

        if not rewrite:
            with open(self.filepath, "rb") as rhdl:
                if rhdl.read() != datas:
                    rewrite = True

        if rewrite:
            with open(self.filepath, "wb") as whdl:
                whdl.write(datas)


class rfc_text(rfc_page):
    def __init__(self, number: int):
        self.__file: str = f"rfc{number}.txt"
        super().__init__(os.path.join("rfc", self.file))

    @property
    def file(self) -> str:
        return self.__file


class rfc_html(rfc_page):
    def __init__(self, number: int):
        self.__file: str = f"rfc{number}.html"
        self.__link: str = os.path.join("rfc", f"rfc{number}")
        super().__init__(os.path.join("rfc", self.file))

    @property
    def file(self) -> str:
        return self.__file

    @property
    def link(self) -> str:
        return self.__link

    def save(self):
        super().save()
        if not os.path.exists(self.link) or os.readlink(self.link) != self.file:  # noqa:E501
            os.symlink(self.file, self.link)


class rfc_pdf(rfc_page):
    def __init__(self, number: int):
        self.__file: str = os.path.join("pdfrfc", f"rfc{number}.txt.pdf")
        super().__init__(self.file, os.path.join("rfc", self.file))

    @property
    def file(self) -> str:
        return self.__file


class rfc():
    def __init__(self, number: int):
        self.__number: int = number

    @property
    def number(self) -> int:
        return self.__number

    @property
    def text(self) -> rfc_text:
        return rfc_text(self.number)

    @property
    def html(self) -> rfc_html:
        return rfc_html(self.number)

    @property
    def pdfrfc(self) -> rfc_pdf:
        return rfc_pdf(self.number)
