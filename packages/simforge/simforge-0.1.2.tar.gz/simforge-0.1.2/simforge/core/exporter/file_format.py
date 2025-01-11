from __future__ import annotations

from enum import Enum, auto
from typing import ClassVar, Iterable, List, Type


class FileFormat(str, Enum):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        FileFormatRegistry.registry.append(cls)

    @staticmethod
    def all_formats() -> Iterable[FileFormat]:
        return (format for formats in FileFormatRegistry.registry for format in formats)

    def __str__(self) -> str:
        return self.name.lower()

    @property
    def ext(self) -> str:
        return f".{self}"

    @classmethod
    def from_ext(cls, ext: str) -> FileFormat:
        try:
            return next(
                format
                for format in cls
                if (ext[1:] if ext.startswith(".") else ext).upper() == format.name
            )
        except StopIteration:
            raise ValueError(f'Extension "{ext}" is not a valid "{cls.__name__}"')

    @classmethod
    def from_ext_any(cls, ext: str) -> FileFormat:
        try:
            return next(
                format
                for format in cls.all_formats()
                if (ext[1:] if ext.startswith(".") else ext).upper() == format.name
            )
        except StopIteration:
            raise ValueError(
                f'Extension "{ext}" is not a valid "{FileFormat.__name__}"'
            )


class FileFormatRegistry:
    registry: ClassVar[List[Type[FileFormat]]] = []


class ImageFileFormat(FileFormat):
    JPG = auto()
    PNG = auto()


class MaterialFileFormat(FileFormat):
    MDL = auto()


class ModelFileFormat(FileFormat):
    ABC = auto()
    FBX = auto()
    GLB = auto()
    GLTF = auto()
    OBJ = auto()
    PLY = auto()
    SDF = auto()
    STL = auto()
    USD = auto()
    USDA = auto()
    USDC = auto()
    USDZ = auto()

    @property
    def ext(self) -> str:
        match self:
            case ModelFileFormat.SDF:
                return ""
            case _:
                return super().ext

    @property
    def supports_material(self) -> bool:
        match self:
            case ModelFileFormat.STL:
                return False
            case _:
                return True
