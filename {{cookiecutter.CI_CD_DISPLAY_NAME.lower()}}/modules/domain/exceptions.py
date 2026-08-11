"""Определяет ожидаемые ошибки прикладного сценария."""


class ApplicationError(Exception):
    """Обозначает ожидаемую ошибку приложения."""


class InputDataError(ApplicationError):
    """Обозначает некорректные входные данные приложения."""


class AssetsSynchronizationError(ApplicationError):
    """Обозначает ошибку переноса поставляемых ресурсов приложения."""


class AssetsSourceNotFoundError(AssetsSynchronizationError):
    """Обозначает отсутствие каталога поставляемых ресурсов."""


class AssetsSourceNotDirectoryError(AssetsSynchronizationError):
    """Обозначает источник ресурсов, который не является каталогом."""


class AssetsSourceReadPermissionError(AssetsSynchronizationError):
    """Обозначает отсутствие прав на чтение каталога поставляемых ресурсов."""


class AssetsDestinationWritePermissionError(AssetsSynchronizationError):
    """Обозначает отсутствие прав на запись в runtime-каталог ресурсов."""


class AssetsDiskSpaceError(AssetsSynchronizationError):
    """Обозначает нехватку места на диске при переносе ресурсов."""
