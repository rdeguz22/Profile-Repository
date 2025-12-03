import json
import boto3
import uuid
from datetime import datetime

sqs = boto3.client('sqs')
QUEUE_URL = 'SQS_QUEUE_URL'

def lambda_handler(event, context):
    try:
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        headers = {k.lower(): v for k, v in headers.items()}
        content_type = headers.get('content-type', '')
        
        if 'application/json' in content_type:
            # Scenario 1: JSON payload
            try:
                payload = json.loads(body)
                tenant_id = payload.get('tenant_id')
                log_id = payload.get('log_id', str(uuid.uuid4()))
                text = payload.get('text', '')
                source = 'json_upload'
                
                if not tenant_id or not text:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'Missing tenant_id or text'})
                    }
                    
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid JSON payload'})
                }
                
        elif 'text/plain' in content_type:
            # Scenario 2: Raw text payload
            tenant_id = headers.get('x-tenant-id')
            
            if not tenant_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing X-Tenant-ID header'})
                }
            
            log_id = str(uuid.uuid4())
            text = body
            source = 'text_upload'
            
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unsupported content type'})
            }
        
        message = {
            'tenant_id': tenant_id,
            'log_id': log_id,
            'text': text,
            'source': source,
            'ingested_at': datetime.utcnow().isoformat()
        }
        
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message),
            MessageAttributes={
                'tenant_id': {
                    'StringValue': tenant_id,
                    'DataType': 'String'
                }
            }
        )
        
        return {
            'statusCode': 202,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Accepted for processing',
                'log_id': log_id,
                'tenant_id': tenant_id
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }