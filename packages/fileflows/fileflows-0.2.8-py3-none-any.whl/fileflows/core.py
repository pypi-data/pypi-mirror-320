import os
import shutil
from functools import cached_property
from pathlib import Path
from typing import List, Optional, Union

from pyarrow import parquet

from .s3 import S3, S3Cfg, is_s3_path


class Files:
    """File operations for local file system and/or s3 protocol object stores."""

    def __init__(self, s3_cfg: Optional[S3Cfg] = None) -> None:
        self.s3_cfg = s3_cfg

    def create(self, location: Union[str, Path]):
        """Create a directory or bucket if it doesn't already exist."""
        # make sure primary save location exists.
        if is_s3_path(location):
            # make sure bucket exists.
            bucket_name, _ = self.s3.bucket_and_partition(
                location, require_partition=False
            )
            self.s3.get_bucket(bucket_name)
        else:
            # make sure directory exists.
            Path(location).mkdir(exist_ok=True, parents=True)

    def copy(self, src_path: Union[str, Path], dst_path: Union[str, Path]):
        """Copy file to a new location."""
        return self._transfer(src_path, dst_path, delete_src=False)

    def move(self, src_path: Union[str, Path], dst_path: Union[str, Path]):
        """Move file to a new location."""
        return self._transfer(src_path, dst_path, delete_src=True)

    def delete(self, file: Union[str, Path], if_exists: bool = False):
        """Delete file."""
        if is_s3_path(file):
            return self.s3.delete_file(file, if_exists=if_exists)
        try:
            Path(file).unlink()
        except FileNotFoundError:
            if not if_exists:
                raise

    def exists(self, file: Union[str, Path]) -> bool:
        """Returns True if file exists."""
        if is_s3_path(file):
            return self.s3.exists(file)
        return os.path.exists(file)

    def file_size(self, file: Union[str, Path]) -> int:
        """Returns file size in bytes."""
        if is_s3_path(file):
            return self.s3.file_size(file)
        return os.path.getsize(file)

    def list_files(
        self, directory: Union[str, Path], pattern: Optional[str] = None
    ) -> Union[List[Path], List[str]]:
        """Returns list of files in directory."""
        if is_s3_path(directory):
            return self.s3.list_files(directory, pattern=pattern)
        if pattern:
            return list(Path(directory).glob(pattern))
        return list(Path(directory).iterdir())

    def parquet_column_names(self, file: Union[str, Path]) -> List[str]:
        """Returns list of column names in parquet file."""
        return list(
            parquet.read_schema(
                file,
                filesystem=self.s3.arrow_fs() if is_s3_path(file) else None,
            ).names
        )

    @cached_property
    def s3(self) -> S3:
        return S3(self.s3_cfg)

    def _transfer(
        self,
        src_path: Union[str, Path],
        dst_path: Union[str, Path],
        delete_src: bool = False,
    ):
        """Move or copy file to a new location."""

        if is_s3_path(src_path):
            if is_s3_path(dst_path):
                self.s3.move(
                    src_path=src_path, dst_path=dst_path, delete_src=delete_src
                )
            else:
                if os.path.isdir(dst_path):
                    dst_path = f"{dst_path}/{Path(src_path).name}"
                self.s3.download_file(
                    s3_path=src_path,
                    local_path=dst_path,
                    overwrite=True,
                )

        elif is_s3_path(dst_path):
            # upload local file to s3.
            bucket_name, partition = self.s3.bucket_and_partition(
                dst_path, require_partition=False
            )
            if not partition:
                partition = str(src_path).split(f"{bucket_name}/")[-1].lstrip("/")
            self.s3.client.upload_file(str(src_path), bucket_name, partition)
        else:
            shutil.copy(src_path, dst_path)
        if delete_src:
            self.delete(src_path)
