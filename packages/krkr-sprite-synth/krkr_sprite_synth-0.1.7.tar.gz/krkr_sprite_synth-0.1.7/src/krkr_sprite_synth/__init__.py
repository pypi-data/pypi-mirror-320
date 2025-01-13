from PIL import Image
from pathlib import Path
from typing import List, Optional

from .drawer import draw
from .models import Layer, ParseResult
from .parser import InfoParser, parse_layers


class SpriteSynth:
    def __init__(
        self,
        a_info_path: str,
        b_info_path: Optional[str],
        layers_info_path_template: str,
        assets_path: str,
        character_name: Optional[str] = None,
    ):
        """初始化 SpriteSynth 类。

        Args:
            a_info_path (str): a_info 文件路径，一般位于 /fgimage/<character_name>a_info.txt
            b_info_path (str, optional): b_info 文件路径，一般位于 /fgimage/<character_name>b_info.txt
            layers_info_path_template (str): 图层信息文件路径模板，一般是 /fgimage/<character_name>/<character_name>{info_type}.txt
            assets_path (str): 资源文件夹路径，一般是 /fgimage/<character_name>
            character_name (str, optional): 角色名，用于辅助查找图层图片. Defaults to None
        """
        self.a_info_path = a_info_path
        self.b_info_path = b_info_path
        self.layers_info_path_template = layers_info_path_template
        self.assets_path = Path(assets_path)
        self.character_name = character_name

        self.a_info = self._read_file(self.a_info_path)
        self.b_info = self._read_file(self.b_info_path) if self.b_info_path else ""

        self.info_parser = InfoParser(a_info=self.a_info, b_info=self.b_info)

    def _read_file(self, file_path: str, encoding: str = "utf-16 LE") -> str:
        """读取指定编码的文件内容。"""
        return Path(file_path).read_text(encoding=encoding).lstrip("\ufeff")

    def get_parse_result(self, dress: str, face: str, pose: str) -> ParseResult:
        """解析给定文件的信息并返回解析结果。"""
        return self.info_parser.parse(dress=dress, face=face, pose=pose)

    def _find_layer(
        self, names: List[str], all_layers: List[Layer], group_id: int = -1
    ) -> Optional[Layer]:
        """Find layer by hierarchical names and group ID.

        Args:
            names: List of layer names forming a path (e.g. ['group1', 'group2', 'layer'])
            all_layers: List of all available layers
            group_id: Parent group layer ID, -1 means root level

        Returns:
            Matching Layer object or None if not found
        """
        current_group_id = group_id

        for i, name in enumerate(names):
            # For each name, find matching layer in current group
            matching_layers = [
                layer
                for layer in all_layers
                if layer.name == name
                and (current_group_id == -1 or layer.group_layer_id == current_group_id)
                and (layer.layer_type == 2 or i == len(names) - 1)
                # layer_type: 0 - layer, 2 - group
            ]

            if not matching_layers:
                print(
                    f"WARN: Cannot find layer {name} in group {current_group_id}, skipping."
                )
                return None

            # Last name in path - return the layer
            if i == len(names) - 1:
                return matching_layers[0]

            # Update group ID for next iteration
            current_group_id = matching_layers[0].layer_id

        return None

    def get_layers(self, layers_info_path: str, names: List[str]) -> List[Layer]:
        """解析图层信息并返回相关图层。"""
        layers_info = self._read_file(layers_info_path)
        all_layers = parse_layers(layers_info=layers_info)

        layers: set[int] = set()

        for name in names:
            layer = self._find_layer(name.split("/"), all_layers)
            layers.add(layer.layer_id) if layer else None

        result = []
        for layer in all_layers:
            if layer.layer_id in layers:
                result.append(layer)

        return result[::-1]

    def draw(self, dress: str, face: str, pose: str) -> Image.Image:
        """绘制立绘

        Args:
            dress (str): 服装名
            face (str): 表情序号
            pose (str): 姿势序号

        Raises:
            ValueError: 如果匹配到的服装数量不为 1 或 2

        Returns:
            Image.Image: 绘制好的立绘
        """
        parse_result = self.get_parse_result(dress=dress, face=face, pose=pose)
        layers_info_path = self.layers_info_path_template.format(
            info_type=parse_result.info_type
        )
        names = parse_result.dresses + parse_result.faces

        layers = self.get_layers(layers_info_path, names)

        return draw(
            layers, parse_result.info_type, self.assets_path, self.character_name
        )


__all__ = ["SpriteSynth"]
