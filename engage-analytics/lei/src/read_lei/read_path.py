from pathlib import Path


class TakePath:

    @staticmethod
    def define_path() -> str:
        """"
        Define the working path
        return Path: string of the opath
        """
        p = Path().absolute()
        path_base = p.parent
        return str(path_base)