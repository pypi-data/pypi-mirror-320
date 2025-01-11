import dataclasses
import os
import shutil


@dataclasses.dataclass
class Workspace:
    """Struct to handle workspace for disk based caching and logging."""

    root: str = os.path.join(
        os.getcwd(), "cache"
    )  # root of workspace (disk based caching)
    workspace: str | None = (
        None  # separated folder to abstract products and logs for different modules.
    )

    def __post_init__(self) -> None:
        """Instantiate workspace

        Returns:
            None
        """
        self.workspace = (
            self.root
            if self.workspace is None
            else os.path.join(self.root, self.workspace)
        )
        os.makedirs(self.root, exist_ok=True)
        os.makedirs(self.workspace, exist_ok=True)

    def __del__(self) -> None:
        """Cleanup after de-allocation of entire obj is done

        Returns:
            None
        """
        if os.path.exists(self.workspace) and not os.listdir(self.workspace):
            shutil.rmtree(self.workspace)
        if os.path.exists(self.root) and not os.listdir(self.root):
            shutil.rmtree(self.root)

    def __str__(self) -> str:
        """Workspace details to string

        Returns:
            str - representation of Workspace class.
        """
        return (
            f"root: {self.root} ({self.disk_memory_allocated(self.root)} bytes);"
            f"workspace: {self.workspace} ({self.disk_memory_allocated(self.workspace)} bytes);"
        )

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def disk_memory_allocated(src: str) -> int:
        """Utility to get disk memory allocated.

        Args:
            src: the root of the dir tree to scan.

        Returns:
            int - space allocated in bytes
        """
        mem_size = 0
        for directory, _, filenames in os.walk(src):
            for f in filenames:
                fp = os.path.join(directory, f)
                if os.path.islink(fp):
                    continue
                mem_size += os.path.getsize(fp)
        return mem_size
