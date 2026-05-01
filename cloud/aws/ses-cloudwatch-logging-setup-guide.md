# AWS SES — CloudWatch Logging Setup Guide

> Get **per-email visibility** for AWS SES (bounce / complaint / delivery) by piping the existing SES → SNS event stream into Lambda → CloudWatch Logs. Catches reputation problems **before** AWS enforces a SHUTDOWN on your account.

**Purpose:** Stand up a serverless logging pipeline that captures every SES event as a JSON log entry in CloudWatch — making it possible to search, alert, and audit per-email outcomes that the SES Console only aggregates.
**Target:** AWS SES + SNS + Lambda + CloudWatch + CloudFormation (one region — example uses `us-east-1`).
**Tested with:** Python 3.12 Lambda runtime, SES v2 API, AWS CloudShell.

[Back to repo root](../../README.md) · [`cloud/aws/`](./README.md) · [Repo conventions](../../AGENTS.md)

---

## Table of contents

1. [Why per-email logging matters](#why-per-email-logging-matters)
2. [Pre-existing setup this guide assumes](#pre-existing-setup-this-guide-assumes)
3. [What gets logged](#what-gets-logged)
4. [Architecture](#architecture)
5. [CloudFormation template](#cloudformation-template)
6. [Deployment — three stacks via AWS CloudShell](#deployment--three-stacks-via-aws-cloudshell)
7. [Verification](#verification)
8. [Resources created (summary)](#resources-created-summary)
9. [SES limits & thresholds reference](#ses-limits--thresholds-reference)
10. [Troubleshooting](#troubleshooting)

---

## Why per-email logging matters

AWS SES gives you **aggregate** metrics in the console (total sends, bounce rate, complaint rate). It does **not** natively store per-email event logs. Without something like the pipeline below, you cannot answer:

- *Which specific email address bounced or complained?*
- *What was the subject line / sender / message ID / timestamp of the failure?*
- *Why didn't user X receive their email yesterday?*
- *Has bounce rate been climbing over the last 24 hours?*
- *Can I retain delivery data for 90 days for audit / compliance?*

> **Real failure mode this prevents:** A bulk send of ~2,000 emails resulting in ~95% bounce rate (bad list, expired addresses) silently triggers an SES auto-SHUTDOWN. With CloudWatch logging in place, the bounce spike shows up in real time and you can pause sends before AWS does it for you.

---

## Pre-existing setup this guide assumes

Before this CloudWatch logging solution can be deployed, the following SES infrastructure must already be in place. **The solution adds Lambdas to an existing event stream — it does not modify SES itself.**

### Existing SNS topic

An SNS topic already receives **all** SES event types from your configuration set:

| Item | Value (example) |
| --- | --- |
| Topic name | `<your-sns-topic-name>` (e.g. `ses-events-prod`) |
| ARN | `arn:aws:sns:us-east-1:<aws-account-id>:<your-sns-topic-name>` |
| Role | Receives ALL SES event types from the configuration set |

### Existing configuration set with event destination

All emails sent from your domain use a **configuration set** (e.g. `common`). That config set already has an **event destination** wired to publish every SES event type to the SNS topic above:

| Event type | Description |
| --- | --- |
| `SEND` | Email accepted by SES for delivery |
| `DELIVERY` | Email successfully delivered to the recipient's mail server |
| `BOUNCE` | Email could not be delivered (hard or soft bounce) |
| `COMPLAINT` | Recipient marked the email as spam |
| `REJECT` | SES rejected the email (e.g. virus content) |
| `DELIVERY_DELAY` | Temporary delivery delay |
| `RENDERING_FAILURE` | Email template failed to render |
| `SUBSCRIPTION` | Recipient updated subscription preferences |

> **Key insight:** Because all events are already flowing to SNS, no SES changes are needed to add CloudWatch logging — only Lambda subscribers on the existing SNS topic.

> **If you don't already have this:** Set up a configuration set in the SES console, add an SNS event destination subscribed to all event types, and create the SNS topic. Once you can see SES events arriving on the topic (Console → SNS → topic → Monitoring), come back here.

---

## What gets logged

Every SES event becomes a structured JSON entry in CloudWatch. Example fields:

| Field | Example |
| --- | --- |
| `notificationType` | `Bounce` / `Complaint` / `Delivery` |
| `bounceType` | `Permanent` / `Transient` |
| `bounceSubType` | `General` / `NoEmail` / `Suppressed` |
| `bouncedRecipients` | List of email addresses that bounced |
| `timestamp` | ISO-8601 UTC, e.g. `2026-02-06T14:38:00.000Z` |
| `messageId` | Unique SES message ID |
| `source` | Sender — `no-reply@<your-domain.com>` |
| `destination` | Recipient list |

---

## Architecture

The solution is a serverless fan-out pipeline. SES already publishes to SNS — this guide only adds Lambdas + CloudWatch.

```
Amazon SES ──(events)──▶ Amazon SNS topic ──(fan-out)──▶ Lambda × 3 ──▶ CloudWatch Logs
                                                          │             │
                                                          │             ├─ /aws/ses/bounce_logs
                                                          ├─ Bounce L.  ├─ /aws/ses/complaint_logs
                                                          ├─ Complaint  └─ /aws/ses/delivery_logs
                                                          └─ Delivery
```

| Component | Role |
| --- | --- |
| **SES** | Sends email, generates events, publishes to the SNS topic configured in the `common` config set |
| **SNS** | Fan-out: receives events from SES, delivers to all subscribers (the 3 Lambdas) |
| **Lambda × 3** | Each Lambda is triggered by SNS, filters by `notificationType`, writes the matching event to its own CloudWatch log group |
| **CloudWatch Logs** | Stores per-event JSON. Searchable, filterable, exportable to S3 for long-term retention. CloudWatch Alarms can fire on bounce-rate spikes |
| **IAM Role** | Each Lambda assumes a role allowing `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` under `/aws/ses/*` |
| **CloudFormation** | Provisions all of the above as a single deployable stack — same template, deployed three times with different parameters |

---

## CloudFormation template

The template is sourced from the official AWS blog: [How to Log Amazon SES details using Amazon CloudWatch](https://aws.amazon.com/blogs/messaging-and-targeting/how-to-log-amazon-ses-details-using-amazon-cloudwatch/).

### Parameters

| Parameter | Description | Allowed values |
| --- | --- | --- |
| `SNSTopicARN` | ARN of the existing SNS topic SES publishes events to | Any valid SNS ARN |
| `EventType` | The SES event type this Lambda will filter and log | `Bounce`, `Complaint`, `Delivery` |
| `CloudWatchGroupName` | The CloudWatch log group where events will be stored | Any valid log group name (default: `/aws/ses/bounce_logs`) |

### Full YAML template

Save as `ses_event_logging.yml` (or use the `cat > ... << 'EOF'` snippet in [Deployment](#deployment--three-stacks-via-aws-cloudshell) below to write it directly inside CloudShell).

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lambda function to log SES events (bounce/complaint/delivery) to CloudWatch'

Parameters:
  CloudWatchGroupName:
    Description: CloudWatch Log Group name for SES notifications.
    Default: /aws/ses/bounce_logs
    Type: String
    AllowedPattern: .+
    ConstraintDescription: CloudWatch Log Group name is required.
  SNSTopicARN:
    Description: ARN of the SNS topic that SES publishes events to.
    Type: String
    AllowedPattern: .+
    ConstraintDescription: SNS Topic ARN is required.
  EventType:
    Description: SES event type to log (Bounce, Complaint, or Delivery).
    Type: String
    Default: Bounce
    AllowedValues:
      - Bounce
      - Complaint
      - Delivery

Resources:
  LambdaRole:
    Type: 'AWS::IAM::Role'
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - lambda.amazonaws.com
            Action:
              - 'sts:AssumeRole'
      Policies:
        - PolicyName: cloudwatch_write_policy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - 'logs:CreateLogGroup'
                  - 'logs:CreateLogStream'
                  - 'logs:PutLogEvents'
                  - 'logs:DescribeLogStreams'
                Resource:
                  - 'arn:aws:logs:*:*:log-group:/aws/ses/*'
      Path: /

  SnsSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      Protocol: lambda
      Endpoint: !GetAtt LambdaFunction.Arn
      TopicArn: !Ref SNSTopicARN

  LambdaInvokePermission:
    Type: AWS::Lambda::Permission
    Properties:
      Action: lambda:InvokeFunction
      Principal: sns.amazonaws.com
      SourceArn: !Ref SNSTopicARN
      FunctionName: !Ref LambdaFunction

  LambdaFunction:
    Type: 'AWS::Lambda::Function'
    DependsOn: LambdaRole
    Properties:
      Environment:
        Variables:
          group_name: !Ref CloudWatchGroupName
          event_type: !Ref EventType
          LOG_LEVEL: 'INFO'
      Role: !GetAtt LambdaRole.Arn
      Timeout: 60
      Handler: index.lambda_handler
      Runtime: python3.12
      MemorySize: 128
      Code:
        ZipFile: |
          import boto3
          import time
          import json
          import sys
          import secrets
          import os
          import logging

          client = boto3.client('logs')

          log_group = os.getenv("group_name")
          event_type = os.getenv("event_type")

          def lambda_handler(event, context):
              global log_level
              log_level = str(os.environ.get('LOG_LEVEL')).upper()
              if log_level not in [
                  'DEBUG', 'INFO',
                  'WARNING', 'ERROR',
                  'CRITICAL'
              ]:
                  log_level = 'ERROR'
              logging.getLogger().setLevel(log_level)

              logging.info(event)

              for record in event['Records']:
                  logs = record['Sns']['Message']
                  logs_data = json.loads(logs)
                  notification_type = logs_data['notificationType']
                  if notification_type == event_type:
                      LOG_GROUP = log_group
                  else:
                      sys.exit()
                  LOG_STREAM = '{}{}{}'.format(
                      time.strftime('%Y/%m/%d'),
                      '[$LATEST]',
                      secrets.token_hex(16)
                  )
                  try:
                      client.create_log_group(logGroupName=LOG_GROUP)
                  except client.exceptions.ResourceAlreadyExistsException:
                      pass
                  try:
                      client.create_log_stream(logGroupName=LOG_GROUP, logStreamName=LOG_STREAM)
                  except client.exceptions.ResourceAlreadyExistsException:
                      pass
                  response = client.describe_log_streams(
                      logGroupName=LOG_GROUP,
                      logStreamNamePrefix=LOG_STREAM
                  )
                  event_log = {
                      'logGroupName': LOG_GROUP,
                      'logStreamName': LOG_STREAM,
                      'logEvents': [
                          {
                              'timestamp': int(round(time.time() * 1000)),
                              'message': logs
                          }
                      ],
                  }
                  if 'uploadSequenceToken' in response['logStreams'][0]:
                      event_log.update({'sequenceToken': response['logStreams'][0]['uploadSequenceToken']})
                  response = client.put_log_events(**event_log)

                  logging.info(response)
```

### Lambda code walkthrough

The embedded function:

- Receives the SNS event (auto-triggered when SNS delivers a message).
- Parses the SES JSON, extracts `notificationType`.
- **Filters by event type** — each Lambda only handles its configured type; exits silently otherwise.
- Creates the CloudWatch log group if it doesn't exist (idempotent).
- Creates a new log stream named `<date>[$LATEST]<random-hex>` for uniqueness.
- Writes the full JSON event to CloudWatch with a UTC millisecond timestamp.

---

## Deployment — three stacks via AWS CloudShell

The same template is deployed **three times** — once per event type. Use AWS CloudShell (browser CLI) so you don't need local AWS CLI setup.

> **Safe in production:** these commands only add resources (Lambda, IAM Role, SNS Subscription, Lambda Permission). They do not modify or remove any existing SES, SNS, or sending configuration.

### 1. Open AWS CloudShell

In the AWS Console (region `us-east-1`), click the **CloudShell** icon (`>_`) in the top nav bar. Wait for the shell to initialize.

### 2. Create the template file in CloudShell

Paste the following — it writes the YAML template to `/tmp/ses_event_logging.yml`:

```bash
cat > /tmp/ses_event_logging.yml << 'EOF'
# (paste the full YAML from the "Full YAML template" section above)
EOF

ls -lh /tmp/ses_event_logging.yml
```

Expected: file exists with non-zero size.

### 3. Deploy stack 1 — Bounce logging

```bash
aws cloudformation create-stack \
  --stack-name ses-bounce-logging \
  --template-body file:///tmp/ses_event_logging.yml \
  --parameters \
    ParameterKey=SNSTopicARN,ParameterValue=arn:aws:sns:us-east-1:<aws-account-id>:<your-sns-topic-name> \
    ParameterKey=EventType,ParameterValue=Bounce \
    ParameterKey=CloudWatchGroupName,ParameterValue=/aws/ses/bounce_logs \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

### 4. Deploy stack 2 — Complaint logging

```bash
aws cloudformation create-stack \
  --stack-name ses-complaint-logging \
  --template-body file:///tmp/ses_event_logging.yml \
  --parameters \
    ParameterKey=SNSTopicARN,ParameterValue=arn:aws:sns:us-east-1:<aws-account-id>:<your-sns-topic-name> \
    ParameterKey=EventType,ParameterValue=Complaint \
    ParameterKey=CloudWatchGroupName,ParameterValue=/aws/ses/complaint_logs \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

### 5. Deploy stack 3 — Delivery logging

```bash
aws cloudformation create-stack \
  --stack-name ses-delivery-logging \
  --template-body file:///tmp/ses_event_logging.yml \
  --parameters \
    ParameterKey=SNSTopicARN,ParameterValue=arn:aws:sns:us-east-1:<aws-account-id>:<your-sns-topic-name> \
    ParameterKey=EventType,ParameterValue=Delivery \
    ParameterKey=CloudWatchGroupName,ParameterValue=/aws/ses/delivery_logs \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

---

## Verification

### 1. Check all 3 stacks deployed

```bash
aws cloudformation describe-stacks --region us-east-1 \
  --query "Stacks[?contains(StackName,'ses')].{Name:StackName,Status:StackStatus}" \
  --output table
```

Expected: all 3 stacks show `CREATE_COMPLETE`.
**Console:** CloudFormation → Stacks → search `ses`.

### 2. Check Lambda functions exist

```bash
aws lambda list-functions --region us-east-1 \
  --query "Functions[?contains(FunctionName,'ses')].{Name:FunctionName,Runtime:Runtime}" \
  --output table
```

**Console:** Lambda → Functions → search `ses` → click each → Triggers tab → confirm SNS trigger present.

### 3. Check CloudWatch log groups exist

```bash
aws logs describe-log-groups --region us-east-1 \
  --log-group-name-prefix /aws/ses \
  --query "logGroups[*].logGroupName"
```

Expected:

```json
[
  "/aws/ses/bounce_logs",
  "/aws/ses/complaint_logs",
  "/aws/ses/delivery_logs"
]
```

### 4. Send a simulated bounce email

AWS provides a **mailbox simulator**. Sending to these addresses triggers a simulated event without affecting real recipients or your reputation:

| Simulator address | Effect |
| --- | --- |
| `bounce@simulator.amazonses.com` | Hard bounce |
| `complaint@simulator.amazonses.com` | Complaint |
| `success@simulator.amazonses.com` | Successful delivery |

```bash
aws sesv2 send-email \
  --from-email-address no-reply@<your-domain.com> \
  --destination ToAddresses=bounce@simulator.amazonses.com \
  --content '{"Simple":{"Subject":{"Data":"Test Bounce"},"Body":{"Text":{"Data":"Test bounce email"}}}}' \
  --configuration-set-name common \
  --region us-east-1
```

> Only works if the SES account is in **active** sending state (not paused/SHUTDOWN). If currently SHUTDOWN due to past bounce/complaint events, request reinstatement via AWS Support before testing.

### 5. Read the resulting CloudWatch log

Wait ~30 seconds, then:

```bash
aws logs tail /aws/ses/bounce_logs --region us-east-1
```

**Console:** CloudWatch → Log groups → `/aws/ses/bounce_logs` → click the latest stream.

You should see something like:

```json
{
  "notificationType": "Bounce",
  "bounce": {
    "bounceType": "Permanent",
    "bounceSubType": "General",
    "bouncedRecipients": [
      { "emailAddress": "bounce@simulator.amazonses.com" }
    ],
    "timestamp": "2026-02-10T12:00:00.000Z",
    "feedbackId": "..."
  },
  "mail": {
    "source": "no-reply@<your-domain.com>",
    "destination": ["bounce@simulator.amazonses.com"],
    "messageId": "..."
  }
}
```

---

## Resources created (summary)

| CloudFormation stack | Event type | Log group |
| --- | --- | --- |
| `ses-bounce-logging` | `Bounce` | `/aws/ses/bounce_logs` |
| `ses-complaint-logging` | `Complaint` | `/aws/ses/complaint_logs` |
| `ses-delivery-logging` | `Delivery` | `/aws/ses/delivery_logs` |

Each stack creates:

- `AWS::IAM::Role` — Lambda execution role allowing writes to `/aws/ses/*` log groups
- `AWS::Lambda::Function` — Python 3.12, 128 MB, 60 s timeout
- `AWS::SNS::Subscription` — subscribes the Lambda to the SNS topic via the Lambda protocol
- `AWS::Lambda::Permission` — grants SNS permission to invoke the Lambda

> All four resources per stack × three stacks = **12 resources total**. None modify SES or the SNS topic itself.

---

## SES limits & thresholds reference

| Metric | Safe | Warning | Critical / shutdown risk |
| --- | --- | --- | --- |
| **Bounce rate** | < 2% | 2% – 5% | > 5% (shutdown likely above 10%) |
| **Complaint rate** | < 0.1% | 0.1% – 0.5% | > 0.5% |
| **Daily send quota** | (account-specific, e.g. 50,000 /day) | — | — |
| **Max send rate** | (account-specific, e.g. 14 /sec) | — | — |

> Your account's exact quota and rate are visible at: SES Console → Account dashboard → Sending statistics.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `CREATE_FAILED` on stack with `MalformedPolicyDocument` | `--capabilities CAPABILITY_IAM` missing | Re-run with the flag |
| Lambda created but no logs ever appear | SES events not actually being published to the SNS topic | In SES → Configuration sets → your set → Event destinations: confirm SNS destination exists with all event types enabled |
| Logs appear for some types but not others | Only one of the 3 Lambdas was deployed, or `EventType` parameter was wrong | Re-check stack parameters — each stack must have its specific `EventType` |
| `bounce@simulator.amazonses.com` send fails with `ProductionAccessNotGranted` | SES is in sandbox mode | Move out of sandbox via SES Console → Account dashboard → Request production access |
| Send fails with `MessageRejected: Email address is not verified` | Sending domain/identity not verified, or sandbox restriction | Verify the domain in SES → Verified identities |
| Lambda runs but no log group is created | IAM role missing `logs:CreateLogGroup` | The bundled IAM role grants this — confirm the stack used the unmodified template |
| Bounce/complaint rate climbs and SES sends a warning email | Reputation problem in your sending list | Use the new logs to identify and suppress the bad recipients quickly; pause non-essential campaigns |

---

## Reference

- [AWS Blog — How to Log Amazon SES details using Amazon CloudWatch](https://aws.amazon.com/blogs/messaging-and-targeting/how-to-log-amazon-ses-details-using-amazon-cloudwatch/)
- [SES — Monitoring using notifications](https://docs.aws.amazon.com/ses/latest/dg/monitor-using-event-publishing.html)
- [SES — Reputation Dashboard](https://docs.aws.amazon.com/ses/latest/dg/monitor-sender-reputation.html)
- [CloudFormation Console — `us-east-1`](https://console.aws.amazon.com/cloudformation/home?region=us-east-1)
- [CloudWatch Log Groups Console — `us-east-1`](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups)
- [SES Console — `us-east-1`](https://console.aws.amazon.com/ses/home?region=us-east-1)
