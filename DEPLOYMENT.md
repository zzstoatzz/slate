# Deploying Slate Memory Server to FastMCP Cloud with S3

This guide explains how to deploy your Slate Memory Server to FastMCP Cloud using S3 for persistent storage.

## Prerequisites

1. AWS S3 bucket created
2. AWS credentials configured
3. FastMCP Cloud account

## What Changed

The SlateDB memory server now supports S3 as a storage backend, allowing it to work in stateless/serverless environments like FastMCP Cloud where disk persistence isn't guaranteed.

### Code Changes Made

1. **Modified `src/slate/mcp_server.py`**:
   - Added S3 configuration via environment variables
   - Automatically uses S3 when `SLATE_S3_BUCKET` is set
   - Falls back to local storage when S3 isn't configured

## Configuration

### Required Environment Variables

Set these environment variables in FastMCP Cloud:

```bash
# Required for S3 storage
SLATE_S3_BUCKET=your-bucket-name

# Optional (defaults shown)
SLATE_S3_PREFIX=slate-memory  # S3 prefix/path for data
```

### AWS Credentials

FastMCP Cloud should handle AWS credentials automatically. If not, you can set:

```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1  # Optional, defaults to us-east-1
```

## Deployment Steps

### 1. Create S3 Bucket

```bash
aws s3 mb s3://your-slate-memory-bucket --region us-east-1
```

### 2. Set Environment Variables in FastMCP Cloud

In your FastMCP Cloud dashboard, add:
- `SLATE_S3_BUCKET`: your-slate-memory-bucket
- `SLATE_S3_PREFIX`: production (or any prefix you prefer)

### 3. Deploy to FastMCP Cloud

```bash
# Push your code (DO NOT push to main directly)
git add .
git commit -m "Add S3 support for FastMCP Cloud deployment"
git push origin your-branch

# Then deploy via FastMCP Cloud dashboard or CLI
```

## Testing S3 Integration Locally

Before deploying, test with your S3 bucket:

```bash
# Set environment variables
export SLATE_S3_BUCKET=your-bucket-name
export SLATE_S3_PREFIX=test

# Run the server
uv run -m slate

# The server will print:
# Using S3 storage: s3://your-bucket-name/test
```

## How It Works

1. **On Startup**: The server checks for `SLATE_S3_BUCKET` environment variable
2. **If S3 is configured**: Uses `slatedb.SlateDB(path, url="s3://bucket/prefix")`
3. **If S3 is not configured**: Falls back to local disk storage
4. **SlateDB handles**: All the complexity of writing to S3, batching writes, and managing the LSM tree

## Benefits

- **Bottomless Storage**: No disk space limits
- **High Durability**: S3's 99.999999999% durability
- **Serverless Compatible**: Works in stateless environments
- **Cost Effective**: Pay only for what you store
- **No Data Loss**: Survives server restarts and redeployments

## Troubleshooting

### Issue: "Access Denied" errors
**Solution**: Ensure your AWS credentials have S3 read/write permissions for your bucket

### Issue: "Bucket not found"
**Solution**: Verify the bucket name and region are correct

### Issue: High latency
**Expected**: S3 has higher latency than local disk. SlateDB mitigates this with batching and caching.

## Next Steps

After deployment:
1. Monitor S3 usage in AWS Console
2. Set up S3 lifecycle policies if needed
3. Consider enabling S3 versioning for additional data protection
4. Set up CloudWatch alarms for monitoring

## Local Development

To develop locally without S3:
```bash
# Simply don't set SLATE_S3_BUCKET
uv run -m slate
# Uses local disk: ./slate_memory
```

To develop with S3:
```bash
export SLATE_S3_BUCKET=dev-bucket
export SLATE_S3_PREFIX=dev-$(whoami)
uv run -m slate
```

## Security Notes

- Never commit AWS credentials to git
- Use IAM roles in production when possible
- Consider encrypting your S3 bucket
- Set up proper S3 bucket policies

## Support

For issues with:
- SlateDB: Check https://slatedb.io/docs/
- FastMCP: Check https://gofastmcp.com/
- This implementation: Check the test file `test_s3_integration.py`