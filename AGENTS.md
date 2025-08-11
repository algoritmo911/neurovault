# Mnemosyne Core Agent Instructions

This document provides instructions for agents working on the Mnemosyne Core project.

## Project Overview

Mnemosyne Core is a next-generation memory management system. The goal of this project is to perform a full upgrade of the core, focusing on stability, scalability, performance, and automation.

## Guiding Principles

*   **Speed and Precision:** Think fast. Act even faster.
*   **Discipline and Detail:** Every module is a brick in the tower. Build it to last.
*   **Automation:** Automate everything that can be automated: testing, deployment, monitoring.

## Development Process

1.  **Branching:**
    *   `main`: Stable, production-ready code. Do not commit directly to `main`.
    *   `dev`: Active development branch. All feature branches are merged into `dev`.
    *   `feature/*` or `feat/*`: Create a new branch for each new feature or module.
2.  **Commits:**
    *   Each commit must be linked to an issue.
    *   Commit messages must be descriptive, with a short subject line and a detailed body if necessary.
3.  **Code Quality:**
    *   All code must be reviewed before merging.
    *   All code must be accompanied by unit and integration tests.
    *   Aim for 90%+ test coverage.
4.  **CI/CD:**
    *   The CI/CD pipeline must pass for all commits.
    *   Any broken build must be fixed within 24 hours.
5.  **Documentation:**
    *   Documentation is a living document and must be kept up-to-date with any changes.

## Project Setup

*   **Language:** Python 3.9+
*   **Dependencies:** Managed in `requirements.txt`.
*   **Structure:**
    *   `src/`: Source code, organized by module.
    *   `tests/`: Unit and integration tests.
    *   `docs/`: Project documentation.
    *   `scripts/`: Automation and deployment scripts.

---

> ⚔️ Katana is watching. Fulfill the will of the upgrade.
