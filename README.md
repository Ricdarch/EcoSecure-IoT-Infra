# 🌐 EcoSecure-IoT-Infra (R&D)

> An end-to-end EcoSecure IoT Infra for Smart Home simulating real IoT environments, processing data locally at the edge, and syncing filtered insights to the cloud.

[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue?logo=githubactions)](https://github.com/features/actions)
[![Orchestration](https://img.shields.io/badge/Orchestration-K3s-yellow?logo=kubernetes)](https://k3s.io/)
[![Cloud](https://img.shields.io/badge/Cloud-AWS-orange?logo=amazonaws)](https://aws.amazon.com/)
[![IaC](https://img.shields.io/badge/IaC-Terraform%20%2B%20Ansible-purple?logo=terraform)](https://www.terraform.io/)
[![License|82](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🎯 Overview

**EcoSecure-IoT Infra** is a full-stack IoT infrastructure project that demonstrates how to build a production-grade edge computing platform from scratch.

The platform simulates a real-world environments:
- 🏢 **Power Distribution Unit** — device used to control the power supply to a data center

Data is processed **locally at the edge** using intelligent filtering rules before only the relevant insights are forwarded to the cloud. This approach reduces bandwidth consumption, cuts cloud costs, enables real-time local decisions, and ensures the system keeps working even without internet connectivity.