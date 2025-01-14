from eo4eu_data_utils.drivers import S3Driver

boto_config = {
    "region_name": "us-east-1",
    "endpoint_url": "",
    "aws_access_key_id": "",
    "aws_secret_access_key": "",
}

if __name__ == "__main__":
    s3_driver = S3Driver(
        config = boto_config,
        bucket = ""
    )

    uploaded = s3_driver.upload_file("local_file.csv", "s3_key.csv")
    if not uploaded:
        print("marmaga")
