#!/usr/bin/env node

const { KmsKeyringNode, buildClient, CommitmentPolicy } = require('@aws-crypto/client-node');

// Retrieve the Base64-encoded encrypted content from command-line arguments
const encryptedBase64 = process.argv[2];
if (!encryptedBase64) {
    console.error('Usage: node decrypt.js <base64_encrypted_content>');
    process.exit(1);
}

// Decode the Base64 string into a Buffer
const encryptedData = Buffer.from(encryptedBase64, 'base64');

// Get the KMS key ARN from the environment variable
const generatorKeyId = process.env.FIELD_LEVEL_KMS_DATA_ENCRYPTION_ARN;
if (!generatorKeyId) {
    console.error('Error: FIELD_LEVEL_KMS_DATA_ENCRYPTION_ARN environment variable is not set.');
    process.exit(1);
}

// Optional: You can add other key ARNs if necessary
const additionalKeyIds = []; // Add if any

// Create the KMS keyring with the retrieved key ARN
const keyring = new KmsKeyringNode({
    generatorKeyId,
    keyIds: additionalKeyIds,
});

const { decrypt } = buildClient(CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT);

(async () => {
    try {
        // Decrypt the data
        const { plaintext } = await decrypt(keyring, encryptedData);
        console.log('Decrypted Content:', plaintext.toString());
    } catch (error) {
        console.error('Decryption failed:', error);
    }
})();
