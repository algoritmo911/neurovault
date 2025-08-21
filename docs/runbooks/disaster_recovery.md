# Runbook: Disaster Recovery

**Objective:** To restore the Mnemosyne Core memory fabric from a survivable snapshot in the event of a total system failure (e.g., database corruption, server loss).

This runbook outlines the high-level process. The actual commands will depend on the final implementation of the command-line interface (CLI) for the `SurvivalKit` and `SnapshotManager` services.

---

### **Prerequisites**

1.  **Access to Keys:** You must have secure access to the private key used for snapshot decryption and signature verification. This key should be stored in a secure location like a hardware wallet or a managed secret store (e.g., Doppler, Vault).
2.  **IPFS Access:** You need access to an IPFS gateway or a local IPFS node to retrieve the snapshot data.
3.  **Latest Snapshot CID:** You must know the IPFS Content Identifier (CID) of the latest known-good snapshot. This should be recorded in a secure, off-site location (e.g., a separate, version-controlled manifest file).
4.  **Clean Application Instance:** A new, running instance of the Mnemosyne Core application, connected to a clean database.

---

### **Recovery Steps**

#### **Step 1: Retrieve the Snapshot from IPFS**

1.  **Identify CID:** Obtain the latest valid snapshot CID from your manifest.
2.  **Download:** Use an IPFS client to download the snapshot artifact.
    ```bash
    # Example command
    ipfs get <LATEST_SNAPSHOT_CID> -o snapshot.encrypted
    ```

#### **Step 2: Decrypt and Verify the Snapshot**

1.  **Decrypt:** Use the `SurvivalKit`'s decryption functionality (exposed via a future CLI) with your private key to decrypt the snapshot.
    ```bash
    # Example command
    mnemosyne-cli survival-kit decrypt --key-file /path/to/private.key --input snapshot.encrypted --output snapshot.signed.json
    ```
2.  **Verify Signature:** Use the `SurvivalKit`'s verification functionality to check the signature of the decrypted snapshot. This ensures the data has not been tampered with.
    ```bash
    # Example command
    mnemosyne-cli survival-kit verify --key-file /path/to/public.key --input snapshot.signed.json
    ```
    If verification fails, **DO NOT PROCEED**. The snapshot is corrupt or tampered with. Try a previous known-good CID.

#### **Step 3: Restore the Snapshot**

1.  **Import Data:** Use the `SnapshotManager`'s restore functionality to import the verified, decrypted snapshot data into the application's database.
    ```bash
    # Example command
    mnemosyne-cli snapshot-manager restore --input snapshot.signed.json
    ```
    This process will populate the database with the events and narratives from the snapshot.

#### **Step 4: Verify the Restoration**

1.  **Restart Services:** Ensure all Mnemosyne Core services are running.
2.  **API Check:** Use the API (e.g., via `curl` or Postman) to query for known data from the snapshot to confirm it's present.
3.  **Health Checks:** Check the application's health endpoints and logs for any errors.

---

**On Failure:** If any step fails, especially decryption or verification, halt the process immediately. The integrity of the memory fabric is paramount. Escalate the issue and attempt to use an older, trusted snapshot.
