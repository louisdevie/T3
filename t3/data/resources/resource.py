import importlib
from pathlib import Path


class Resource:
    def __init__(self, path):
        path = Path(path)
        # if not path.is_absolute():
        #     path = self.__base_dir / path

        name = "qrc." + path.stem

        loader = importlib.machinery.SourceFileLoader(name, str(path))
        spec = importlib.util.spec_from_loader(name, loader)
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise Exception(f"can't load resource “{name}”: {e}")

        for required_attr in (
            "qt_resource_data",
            "qt_resource_name",
            "qt_resource_struct",
            "qInitResources",
            "qCleanupResources",
        ):
            if not hasattr(module, required_attr):
                raise Exception(
                    f"can't load resource “{name}”: {required_attr} not found"
                )

        self.__unloader = module.qCleanupResources
