import boto3
import uuid
from botocore.exceptions import ClientError


class S3Utils:
    @classmethod
    def path_to_parts(self, path) -> tuple[str, str]:
        if path.startswith("s3://"):
            path = path[5:]
        b = path.find("/")
        bucket = path[0:b]
        key = path[b + 1 :]
        return (bucket, key)

    @classmethod
    def exists(self, bucket: str, key: str) -> bool:
        client = boto3.client("s3")
        try:
            import warnings

            warnings.filterwarnings(
                action="ignore", message=r"datetime.datetime.utcnow"
            )
            client.head_object(Bucket=bucket, Key=key)

        except ClientError as e:
            assert str(e).find("404") > -1
            return False
        except DeprecationWarning:
            ...
        return True

    @classmethod
    def remove(self, bucket: str, key: str) -> None:
        #
        # see csvpath.util.Nos.remove() for a remove that deletes all children.
        # s3 children are essentially completely independent of their
        # notionally containing parents.
        #
        client = boto3.client("s3")
        client.delete_object(Bucket=bucket, Key=key)

    @classmethod
    def copy(self, bucket: str, key: str, new_bucket: str, new_key: str) -> None:
        client = boto3.client("s3")
        client.copy_object(
            Bucket=new_bucket,
            CopySource={"Bucket": bucket, "Key": key},
            Key=new_key,
            ChecksumAlgorithm="SHA256",
        )

    @classmethod
    def rename(self, bucket: str, key: str, new_key: str) -> None:
        """
        client = boto3.client("s3")
        r = client.copy_object(
            Bucket=bucket,
            CopySource={'Bucket': bucket, 'Key': key},
            Key=new_key,
            ChecksumAlgorithm='SHA256'
        )
        """
        S3Utils.copy(bucket, key, bucket, new_key)
        S3Utils.remove(bucket, key)
