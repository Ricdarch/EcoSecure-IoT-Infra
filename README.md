# 🌐 EcoSecure-IoT-Infra (R&D)

> An end-to-end EcoSecure IoT Infra for Smart Home simulating real IoT environments, processing data locally at the edge, and syncing filtered insights to the cloud.

[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue?logo=githubactions)](https://github.com/features/actions)
[![Orchestration](https://img.shields.io/badge/Orchestration-K3s-yellow?logo=kubernetes)](https://k3s.io/)
[![Cloud](https://img.shields.io/badge/Cloud-AWS-orange?logo=amazonaws)](https://aws.amazon.com/)
[![IaC](https://img.shields.io/badge/IaC-Terraform%20%2B%20Ansible-purple?logo=terraform)](https://www.terraform.io/)
[![License|82](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 📖 Table of Contents

- [Overview](#-overview)
- [Why Edge Computing?](#-why-edge-computing)
- [Architecture](#-architecture)
- [Use Cases](#-use-cases)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Modules](#-modules)
- [Getting Started](#-getting-started)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Observability](#-observability)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 Overview

**EcoSecure-IoT Infra** is a full-stack IoT infrastructure project that demonstrates how to build a production-grade edge computing platform from scratch.

The platform simulates a real-world environments:
- 🏢 **Power Distribution Unit** — device used to control the power supply to a data center

Data is processed **locally at the edge** using intelligent filtering rules before only the relevant insights are forwarded to the cloud. This approach reduces bandwidth consumption, cuts cloud costs, enables real-time local decisions, and ensures the system keeps working even without internet connectivity.

---

## 💡 Why Edge Computing?

Traditional IoT architectures send all raw data to the cloud for processing. This creates several problems at scale:

| Problem | Cloud-only | Edge Computing |
|---|---|---|
| **Latency** | 100–500ms round trip | <5ms local processing |
| **Bandwidth** | All raw data uploaded | Only filtered data sent |
| **Cost** | High cloud ingestion fees | Drastically reduced |
| **Resilience** | Offline = no processing | Works without internet |
| **Privacy** | All data leaves the site | Sensitive data stays local |
| **Real-time alerts** | Delayed by cloud roundtrip | Instant local triggering |

With thousands of sensors running 24/7 in a factory or across a smart home fleet, the difference is massive — both in performance and operating cost.

---

## 🏗️ Architecture

### High-Level Overview

Test