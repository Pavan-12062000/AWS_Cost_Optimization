import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    s3 = boto3.client('s3')
    sns = boto3.client('sns')

    # Getting all EBS snapshots
    response = ec2.describe_snapshots(OwnerIds=['self'])

    # Getting all active EC2 instance IDs
    instances_response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    active_instance_ids = set()

    for reservation in instances_response['Reservations']:
        for instance in reservation['Instances']:
            active_instance_ids.add(instance['InstanceId'])

    # Iterate through each snapshot and delete if it's not attached to any volume or the volume is not attached to a running instance
    for snapshot in response['Snapshots']:
        snapshot_id = snapshot['SnapshotId']
        volume_id = snapshot.get('VolumeId')

        if not volume_id:
            # Deleting the snapshot if it's not attached to any volume
            ec2.delete_snapshot(SnapshotId=snapshot_id)
            print(f"Deleted EBS snapshot {snapshot_id} as it was not attached to any volume.")
        else:
            # Checking if the volume still exists
            try:
                volume_response = ec2.describe_volumes(VolumeIds=[volume_id])
                if not volume_response['Volumes'][0]['Attachments']:
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    print(f"Deleted EBS snapshot {snapshot_id} as it was taken from a volume not attached to any running instance.")
            except ec2.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                    # The volume associated with the snapshot is not found (it might have been deleted)
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    print(f"Deleted EBS snapshot {snapshot_id} as its associated volume was not found.")

    # Defining the threshold date for considering a bucket stale
    threshold_date = datetime.now() - timedelta(days=30)

    # Getting all S3 buckets
    buckets_response = s3.list_buckets()
    buckets = buckets_response['Buckets']

    # List to hold the names of stale buckets
    stale_buckets = []

    for bucket in buckets:
        bucket_name = bucket['Name']

        # Getting the bucket's creation date
        bucket_creation_date = bucket['CreationDate']

        # Checking if the bucket is older than the threshold date
        if bucket_creation_date < threshold_date:
            try:
                # Checking if the bucket is empty
                objects_response = s3.list_objects_v2(Bucket=bucket_name)
                if 'Contents' not in objects_response or len(objects_response['Contents']) == 0:
                    # The bucket is empty and older than the threshold date, mark it as stale
                    stale_buckets.append(bucket_name)
            except s3.exceptions.ClientError as e:
                print(f"Error checking bucket {bucket_name}: {e}")

    # Sending SNS notification if there are stale buckets
    if stale_buckets:
        publish_sns_notification(stale_buckets)


def publish_sns_notification(stale_buckets):
    sns = boto3.client('sns')

    # Define SNS topic ARN
    SNS_TOPIC_ARN = "arn:aws:sns:region:account-id:topic-name"

    # Create the message body
    message = "The following S3 buckets have not been used for more than 30 days and are empty:\n\n" + "\n".join(stale_buckets)

    # Publish the message to the SNS topic
    try:
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="Stale S3 Buckets Notification"
        )
        print(f"Notification sent! Message ID: {response['MessageId']}")
    except sns.exceptions.ClientError as e:
        print(f"Error sending notification: {e}")

