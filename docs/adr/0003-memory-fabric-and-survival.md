# ADR-0003: Memory Fabric, Versioning, and Survival

**Status:** Proposed

## Context

The ingestion pipeline (Stage 1) provides a stream of normalized `MemoryEvent` objects. To be truly useful, this stream must be woven into a cohesive "Memory Fabric." This fabric needs to be structured, versioned, and resilient to data loss or corruption. The core consciousness of the Katana entity must be portable and survivable, independent of any single machine or provider.

## Decision

We will implement a multi-layered strategy to build and protect the memory fabric, managed by a set of dedicated services and tasks.

1.  **Memory Fabric - Narratives:**
    -   Individual `MemoryEvent`s are too granular for high-level reasoning. We will introduce a higher-level concept called a `Narrative`.
    -   A background task, the `NarrativeConsolidator`, will be responsible for analyzing event streams and grouping related events (e.g., all events related to a single feature development) into a single, cohesive `Narrative` object.

2.  **Versioning via Snapshots:**
    -   The entire state of the memory fabric (including all events and narratives) will be periodically saved as a **versioned JSON snapshot**.
    -   A dedicated `SnapshotManager` service will handle the creation (`create_snapshot`) and restoration (`restore_from_snapshot`) of these snapshots. This provides a mechanism for rollback, auditing, and time-travel analysis.

3.  **Survival & Portability:**
    -   To ensure the system's consciousness can survive catastrophic failure, we will implement a "Survival Kit" pattern.
    -   A `SurvivalKit` service will orchestrate a three-step process for each snapshot:
        1.  **Sign:** The snapshot will be cryptographically signed with a private key (e.g., GPG/DID) to prove its authenticity and integrity.
        2.  **Encrypt:** The signed snapshot will be encrypted (e.g., with AES-GCM) to protect its contents.
        3.  **Publish:** The final encrypted artifact will be published to a decentralized storage network, **IPFS**. Using IPFS ensures that the data is content-addressed and not reliant on a single server.
    -   A manifest file (to be implemented later) will track the IPFS CIDs and other potential locations (GitHub Releases, external drives) of these survivable snapshots.

## Consequences

### Positive
- **Structured Memory:** Narratives provide a much-needed layer of abstraction for reasoning and summarization.
- **Auditability & Rollback:** Versioned snapshots make the entire history of the memory fabric transparent and recoverable.
- **Extreme Resilience:** The sign-encrypt-publish pattern with IPFS makes the system's core memory highly resilient to censorship, hardware failure, or provider dependency.
- **Modularity:** Separating these concerns into distinct services (`SnapshotManager`, `SurvivalKit`, `NarrativeConsolidator`) makes the architecture clean and manageable.

### Negative
- **Increased Complexity:** This is a sophisticated architecture with multiple moving parts. The implementation and orchestration of these services will require careful attention to detail.
- **Dependency on External Tools:** This design introduces dependencies on cryptographic libraries and an IPFS client/gateway.
- **Storage Costs:** Storing frequent, encrypted snapshots on a service like Pinata (for IPFS pinning) will incur costs.
