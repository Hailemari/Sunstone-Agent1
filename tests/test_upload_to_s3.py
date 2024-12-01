import os
import unittest
from unittest.mock import patch, MagicMock
from moto import mock_aws
import boto3
from scripts.upload_to_s3 import upload_audio_files
from config.aws_config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, S3_BUCKET_NAME


class TestUploadToS3(unittest.TestCase):
    @mock_aws
    def setUp(self):
        """Set up a mock S3 environment."""
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION,
        )
        self.s3.create_bucket(Bucket=S3_BUCKET_NAME)

        # Create a test audio folder
        self.test_audio_folder = "test_audio"
        os.makedirs(self.test_audio_folder, exist_ok=True)
        self.test_file = os.path.join(self.test_audio_folder, "test.mp3")
        with open(self.test_file, "w") as f:
            f.write("This is a test audio file.")

    @mock_aws
    def tearDown(self):
        """Clean up the test environment."""
        if os.path.exists(self.test_audio_folder):
            for file in os.listdir(self.test_audio_folder):
                os.remove(os.path.join(self.test_audio_folder, file))
            os.rmdir(self.test_audio_folder)

    @mock_aws
    def test_upload_audio_files(self):
        """Test the upload_audio_files function."""
        # Mock S3 client
        s3_mock = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION,
        )

        # Run the upload_audio_files function
        upload_audio_files(self.test_audio_folder)

        # Verify the file was uploaded to S3
        response = s3_mock.list_objects_v2(Bucket=S3_BUCKET_NAME)
        self.assertIn("Contents", response)
        uploaded_files = [obj["Key"] for obj in response["Contents"]]
        self.assertIn("audio/test.mp3", uploaded_files)

    @mock_aws
    @patch("scripts.upload_to_s3.boto3.client")
    def test_upload_failure(self, mock_boto_client):
        """Test upload failure handling."""
        # Mock S3 client to throw an exception
        mock_boto_client().upload_file.side_effect = Exception("Mock upload failure")

        with self.assertLogs(level="ERROR") as log:
            upload_audio_files(self.test_audio_folder)
            self.assertTrue(any("Failed to upload" in message for message in log.output))


if __name__ == "__main__":
    unittest.main()