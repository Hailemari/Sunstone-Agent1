import os
import boto3
from config.aws_config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, S3_BUCKET_NAME

def upload_audio_files(audio_folder):
    """Uploads all audio files in the specified folder to the AWS S3 bucket."""
    # Initialize the S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )

    # Track if any files were uploaded
    files_uploaded = False

    # Loop through all files in the audio folder
    for root, _, files in os.walk(audio_folder):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                s3_key = f"audio/{file}"  # S3 key (path in bucket)

                try:
                    # Upload the file to S3
                    s3_client.upload_file(file_path, S3_BUCKET_NAME, s3_key)
                    print(f"Uploaded: {file_path} to s3://{S3_BUCKET_NAME}/{s3_key}")
                    files_uploaded = True
                except Exception as e:
                    print(f"Failed to upload {file_path}: {e}")

    if not files_uploaded:
        print("No .mp3 files were found in the specified directory.")

if __name__ == "__main__":
    audio_folder = "../audio/"  # Relative path to the audio folder
    upload_audio_files(audio_folder)
