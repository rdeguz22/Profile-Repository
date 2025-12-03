import json
import boto3
import time
import re
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'ProcessedLogs'
table = dynamodb.Table(TABLE_NAME)

def redact_phone_numbers(text):
    """
    Redact phone numbers from text
    """
    pattern = r'\b\d{3}[-.]?\d{4}\b'
    return re.sub(pattern, '[REDACTED]', text)

def lambda_handler(event, context):
    """
    Worker function that processes messages from SQS
    Simulates heavy processing with sleep
    Stores results in DynamoDB with multi-tenant isolation
    """
    
    for record in event['Records']:
        try:
            message = json.loads(record['body'])
            
            tenant_id = message['tenant_id']
            log_id = message['log_id']
            text = message['text']
            source = message['source']
            ingested_at = message['ingested_at']
            
            char_count = len(text)
            sleep_time = char_count * 0.05
            
            print(f"Processing log {log_id} for tenant {tenant_id}: {char_count} chars, sleeping {sleep_time}s")
            time.sleep(sleep_time)
            
            modified_data = redact_phone_numbers(text)
            
            item = {
                'tenant_id': tenant_id,
                'log_id': log_id,
                'source': source,
                'original_text': text,
                'modified_data': modified_data,
                'char_count': char_count,
                'processing_time': sleep_time,
                'ingested_at': ingested_at,
                'processed_at': datetime.utcnow().isoformat()
            }
            
            table.put_item(Item=item)
            
            print(f"Successfully processed and stored log {log_id} for tenant {tenant_id}")
            
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            raise e
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }