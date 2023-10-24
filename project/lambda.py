import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key'] # file path
    bucket = event['s3_bucket'] # s3 bucket

    # Download the data from s3 to /tmp/image.png
    s3=boto3.resource('s3')
    s3.Object(bucket, key).download_file('/tmp/image.png')

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

################################################################################

import os
import io
import boto3
import json
import base64

# grab environment variables
ENDPOINT_NAME = 'scones-bike-motorcycle-classifier-2023-10-22-08-27'
runtime= boto3.client('runtime.sagemaker')

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event["body"]["image_data"])

    # Instantiate a Predictor
    response = runtime.invoke_endpoint(
                                        EndpointName=ENDPOINT_NAME,    
                                        Body=image,               
                                        ContentType='image/png'
                                    )
                                    
    
    # Make a prediction
    inferences = json.loads(response['Body'].read().decode('utf-8'))
  
    
    # We return the data back to the Step Function    
    event['inferences'] = inferences                        
    return {
        'statusCode': 200,
        'body': event
    }






################################################################################

import json

THRESHOLD = .93

def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event['body']["inferences"]## TODO: fill in
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = False ## TODO: fill in
    for i in inferences:
        if i >= THRESHOLD:
            meets_threshold = True
            
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        Exception("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }