import boto3
import os
from PIL import Image
import io

s3 = boto3.client('s3')

# Destination bucket name (change this to your actual processed bucket)
PROCESSED_BUCKET = 'processed-bucket-name'

def lambda_handler(event, context):
    try:
        # Get the uploaded image's details
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']
        
        # Download the image from the source S3 bucket
        image_obj = s3.get_object(Bucket=source_bucket, Key=object_key)
        image_data = image_obj['Body'].read()
        
        # Open the image using Pillow
        img = Image.open(io.BytesIO(image_data))

        # Resize and reduce quality (adjust dimensions as needed)
        img = img.resize((int(img.width * 0.5), int(img.height * 0.5)))  # 50% smaller

        # Save to a buffer in JPEG format with reduced quality
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=60)
        buffer.seek(0)
        
        # Upload to the processed bucket
        s3.put_object(Bucket=PROCESSED_BUCKET, Key=object_key, Body=buffer, ContentType='image/jpeg')

        return {
            'statusCode': 200,
            'body': f"Successfully processed {object_key}"
        }

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error processing image: {str(e)}"
        }
