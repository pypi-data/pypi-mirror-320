#!/bin/bash

# Install pgcli if not installed
if ! command -v pgcli &> /dev/null; then
    echo "pgcli not found. Installing..."
    pip3 install --break-system-packages pgcli || { echo "Failed to install pgcli"; exit 1; }
else
    echo "pgcli is already installed."
fi

# Set environment variables
export DB_HOST_NAME=$DATABASE_HOST
export DB_NAME=$DATABASE_NAME
export LD_LIBRARY_PATH=""
export SECRET_NAME=$DB_ACCESS_SECRET_NAME
export AWS_REGION=$(echo $DB_HOST_NAME | grep -oP '\.\K[a-z]{2}-[a-z]+-\d')

# Fetch the secret using Node.js and store USER and PASSWORD
eval $(node -e "
  const { SecretsManager } = require('@aws-sdk/client-secrets-manager');
  const secretName = process.env.SECRET_NAME;

  // Use the extracted region from DATABASE_HOST
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
    }
  }

  fetchSecret();
")

# Call the pgcli command using the variables
pgcli "postgres://$USER:$PASSWORD@$DB_HOST_NAME:5432/$DB_NAME?sslmode=require"
