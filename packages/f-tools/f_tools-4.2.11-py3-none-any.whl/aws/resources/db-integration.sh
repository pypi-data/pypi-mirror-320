#!/bin/bash

# Required for aws lambda image
export LD_LIBRARY_PATH=""

# Check if pgcli is installed
if ! command -v pgcli &> /dev/null; then
  echo "pgcli is not installed. Installing dependencies and pgcli..."
  dnf install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel libpcap-devel xz-devel libpq-devel python3
  python3 -m ensurepip
  pip3 install pgcli
else
  echo "pgcli is already installed."
fi

# Set environment variables
export DB_HOST_NAME=$DB_HOST_NAME
export DB_NAME=$DB_NAME
export SECRET_NAME=$DB_ACCESS_SECRET
export AWS_REGION=$(echo $DB_HOST_NAME | grep -oP '\.\K[a-z]{2}-[a-z]+-\d')

# Fetch the secret using Node.js and store USER and PASSWORD
eval $(node -e "
  const { SecretsManager } = require('@aws-sdk/client-secrets-manager');
  const secretName = process.env.SECRET_NAME;

  // Use the extracted region from DB_HOST_NAME
  const region = process.env.AWS_REGION;
  const client = new SecretsManager({ region });

  async function fetchSecret() {
    try {
      const data = await client.getSecretValue({ SecretId: secretName });
      const secret = JSON.parse(data.SecretString);
      const USER = secret.id;
      const PASSWORD = secret.password;

      // Output USER and PASSWORD as bash exportable variables
      console.log(\`USER=\${USER}\`);
      console.log(\`PASSWORD=\${PASSWORD}\`);
    } catch (error) {
      console.error('Error fetching secret:', error);
      process.exit(1);
    }
  }

  fetchSecret();
")

# Call the pgcli command using the variables
pgcli "postgres://$USER:$PASSWORD@$DB_HOST_NAME:5432/$DB_NAME?sslmode=require"
