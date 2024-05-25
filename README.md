# AWS Lambda Function for Managing EBS Snapshots and S3 Buckets

## Description
The Lambda function gathers all EBS snapshots owned by the account ('self') and lists all active EC2 instances (both running and stopped). It then checks each snapshot to see if its associated volume (if any) is connected to an active instance. If a snapshot is found to be stale, it is deleted to help reduce storage costs. Additionally, it identifies S3 buckets that have not been used for more than 30 days and are empty and sends a notification about these stale buckets using Amazon SNS and SQS.

## Features
- **EBS Snapshot Management**: Identifies and deletes EBS snapshots that are not associated with any active EC2 instance to save on storage costs.
- **S3 Bucket Notification**: Identifies S3 buckets that have been empty and unused for more than 30 days and sends a notification about these buckets using SNS and SQS.

## Prerequisites
- AWS Account with appropriate permissions.
- AWS Lambda, EC2, S3, SNS, and SQS services set up.
- IAM Role with the necessary permissions assigned to the Lambda function.

## Setup

### Create an SQS Queue
1. Go to the [SQS console](https://console.aws.amazon.com/sqs/v2/home).
2. Create a new queue and note its URL and ARN.

### Create an SNS Topic
1. Go to the [SNS console](https://console.aws.amazon.com/sns/v3/home).
2. Create a new topic and note the ARN.

### Subscribe the SQS Queue to the SNS Topic
1. In the SNS console, select your topic and click on "Create subscription".
2. Choose "SQS" as the protocol and enter the ARN of your SQS queue.
3. Confirm the subscription.

### Subscribe Email Addresses to the SNS Topic (Optional)
1. In the SNS console, select your topic and click on "Create subscription".
2. Choose "Email" as the protocol and enter the email addresses you want to notify.
3. Confirm the subscriptions by clicking on the confirmation links sent to the email addresses.

### Lambda Function Code

Deploy the Lambda function code to your AWS Lambda service
