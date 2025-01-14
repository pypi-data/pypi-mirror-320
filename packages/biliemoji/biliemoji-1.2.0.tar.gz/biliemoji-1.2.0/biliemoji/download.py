from pathlib import Path
from tkinter import NO
from requests import request
import json
from threading import Thread, get_ident
from enum import Enum
from loguru import logger
from time import sleep
import re


class PartID(Enum):
    """分类 表情包-0 装扮-1

    Args:
        Enum (_type_): 枚举类型
    """

    EMOJI = 0
    DRESS = 1
    GIF = 2
    VIDEO = 3


class MultiTDownload:
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(
        self, model: PartID, input_path: Path, output_path: Path, proxies: dict = {}
    ) -> None:
        """构造函数

        Args:
            model (PartID): 选择一个下载模式：表情包/装扮
            input_path (Path): 输入路径
            output_path (Path): 输出路径
            proxies (dict, optional): 代理. Defaults to {}.
        """
        self.input_path = input_path
        self.output_path = output_path
        self.proxies = proxies
        self.model = model

    def check_file(self) -> None:
        """检查文件是否存在，是否为json文件

        Raises:
            TypeError: 不是json文件
            ValueError: 文件不存在
        """
        if self.input_path.suffix != ".json":
            raise TypeError(f"{self.input_path} 文件非json格式")

        if not self.input_path.exists():
            raise ValueError("文件不存在")

    def start(self) -> None:
        """下载主入口"""
        self.check_file()
        if self.model.value == 0:
            self.emoji_download(
                input_path=self.input_path, output_path=self.output_path
            )
        elif self.model.value == 1:
            self.dress_download(
                input_path=self.input_path, output_path=self.output_path
            )
        elif self.model.value == 2:
            self.gif_download(input_path=self.input_path, output_path=self.output_path)
        elif self.model.value == 3:
            self.video_download(
                input_path=self.input_path, output_path=self.output_path
            )

    def emoji_download(self, input_path: Path, output_path: Path) -> None:
        """表情包下载

        Args:
            input_path (Path): 输入json文件
        """
        input_path = self.input_path
        output_path = self.output_path
        with open(input_path, "r", encoding="UTF-8") as f:
            data = json.loads(f.read())

        # 通过表情包的名称分类
        folder_name = Path.joinpath(output_path, data["data"]["packages"][0]["text"])

        if not Path(folder_name).exists():
            Path(folder_name).mkdir()

        # 开始下载
        for i in data["data"]["packages"]:
            for j in i["emote"]:
                url = j["url"]
                file_name = j["text"]

                file_name = self.sanitize_filename(filename=file_name)

                # 文件存在无需重复下载
                if Path.joinpath(folder_name, f"{file_name}.png").exists():
                    logger.warning(f"{file_name}.png已存在")
                    continue

                # 创建线程并启动
                t = Thread(
                    target=self.download,
                    args=(url, Path.joinpath(folder_name, f"{file_name}.png")),
                )
                t.start()

    def gif_download(self, input_path: Path, output_path: Path) -> None:
        input_path = self.input_path
        output_path = self.output_path
        with open(input_path, "r", encoding="UTF-8") as f:
            data = json.loads(f.read())

        try:
            data["data"]["packages"][0]["meta"]["label_text"]
        except:
            raise ValueError("不是gif文件")

        # 通过表情包的名称分类
        folder_name = Path.joinpath(output_path, data["data"]["packages"][0]["text"])

        if not Path(folder_name).exists():
            Path(folder_name).mkdir()

        # 开始下载
        for i in data["data"]["packages"]:
            for j in i["emote"]:
                # 改为gif_url
                url = j["gif_url"]
                file_name = j["text"]

                file_name = self.sanitize_filename(filename=file_name)

                # 文件存在无需重复下载
                if Path.joinpath(folder_name, f"{file_name}.gif").exists():
                    logger.warning(f"{file_name}.gif已存在")
                    continue

                # 创建线程并启动
                t = Thread(
                    target=self.download,
                    args=(url, Path.joinpath(folder_name, f"{file_name}.gif")),
                )
                t.start()

    def video_download(self, input_path: Path, output_path: Path) -> None:
        input_path = self.input_path
        output_path = self.output_path
        with open(input_path, "r", encoding="UTF-8") as f:
            data = json.loads(f.read())

        folder_name = Path.joinpath(output_path, data["data"]["name"])
        if not folder_name.exists():
            folder_name.mkdir()

        # print(f"输出路径：{folder_name}");

        for i in data["data"]["item_list"]:
            try:
                video_url = i["card_info"]["video_list"][0]
                # print(video_url)
            except:
                continue

            name = i["card_info"]["card_name"]
            name = self.sanitize_filename(name)

            file_name = Path.joinpath(folder_name, f"{name}.mp4")

            # print(file_path)

            if Path(file_name).exists():
                logger.warning(f"{file_name}已存在")
                continue

            # 创建线程并启动
            t = Thread(
                target=self.download,
                args=(video_url, file_name),
            )
            t.start()

    def dress_download(self, input_path: Path, output_path: Path) -> None:
        """装扮下载

        Args:
            input_path (Path): 输入json文件
        """
        input_path = self.input_path
        output_path = self.output_path

        with open(input_path, "r", encoding="UTF-8") as f:
            data = json.loads(f.read())

        # emoji_dir = Path.joinpath(self.output_path, "收藏集")

        folder_name = Path.joinpath(output_path, data["data"]["name"])
        if not folder_name.exists():
            folder_name.mkdir()

        # print(f"输出路径：{folder_name}");

        for i in data["data"]["item_list"]:
            url = i["card_info"]["card_img_download"]
            name = i["card_info"]["card_name"]
            name = self.sanitize_filename(name)

            file_name = Path.joinpath(folder_name, f"{name}.png")

            # print(file_path)

            if Path(file_name).exists():
                logger.warning(f"{file_name}已存在")
                continue

            # 创建线程并启动
            t = Thread(
                target=self.download,
                args=(url, file_name),
            )
            t.start()

    def download(self, url: str, filename: Path) -> None:
        """下载函数

        Args:
            url (str): 下载链接
            filename (str): 保存文件名
        """
        r = request("GET", url, headers=self.headers, proxies=self.proxies)

        sleep(1)

        with open(filename, "wb") as f:
            logger.info(f"正在下载{filename}...")
            f.write(r.content)

    def sanitize_filename(self, filename: str) -> str:
        """将文件名中的非法字符换为_

        Args:
            filename (str): 文件名

        Returns:
            str: 替换后的文件名
        """
        # 定义Windows不允许的字符
        invalid_chars = r'<>:"/\|*?'

        # 使用下划线替换非法字符
        sanitized_filename = re.sub(invalid_chars, " ", filename)
        return sanitized_filename
