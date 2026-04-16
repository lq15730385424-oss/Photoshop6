---
name: openaccountants
description: "Classify bank transactions by VAT category and prepare tax return working papers. Covers 134 countries with downloadable country-specific skill packs."
risk: safe
source: community
date_added: "2026-04-16"
---

# OpenAccountants

## Overview

Open-source library of tax computation skills maintained at [openaccountants/openaccountants](https://github.com/openaccountants/openaccountants). Each country package contains markdown skill files for VAT/GST classification, income tax, social security contributions, and guided intake. Upload the relevant country files alongside a bank statement to classify transactions and produce working papers.

## When to Use This Skill

- Classifying bank transactions by VAT category for a specific country.
- Preparing VAT return working papers from bank statements.
- Onboarding a new client with guided tax intake questions.
- Checking which tax rules apply to a transaction in an unfamiliar jurisdiction.

## How It Works

1. **Download** the country package from the [OpenAccountants repo](https://github.com/openaccountants/openaccountants) (e.g., `countries/mt/` for Malta, `countries/gb/` for UK).
2. **Upload** the country skill files alongside your bank statement to Claude or any LLM.
3. **Classify** — the skills guide the LLM through transaction classification using local tax rules.
4. **Review** — output is a working paper with categorized transactions ready for accountant sign-off.

## Coverage

- **8 countries** with full guided experience (VAT + income tax + SSC + guided intake): Malta, UK, Germany, Australia, Canada, India, Spain, US-California.
- **27 countries** with multi-skill coverage (VAT + income tax + SSC).
- **99 countries** with VAT/GST classification.
- **134 countries** total, **371 skills**.

## Limitations

- Skills are markdown-based instructions, not executable tax calculators — the LLM performs the reasoning.
- Quality tiers vary: Q1 (battle-tested), Q2 (research-verified), Q3 (AI-drafted, not independently verified).
- Country coverage is community-driven — some jurisdictions may have outdated or incomplete rules.
- Always have a qualified accountant review the output before filing.
