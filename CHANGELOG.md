# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-08-28

### Added

- Added tabbed spreadsheet workflows with workbook previews and table inference.
- Added workbook discovery, worksheet selection, NDJSON conversion, and product usage timeline skills.
- Added token-aware workbook processing and continuous monthly product usage timelines.

### Changed

- Replaced legacy spreadsheet skills and tools with focused workbook workflows.
- Centralized workbook helpers and adopted platform-specific data paths.

## [0.1.2] - 2026-08-16

### Added

- Added project code, live demo, paper, and model links to the README.

## [0.1.1] - 2026-08-16

### Added

- Added project code, live demo, paper, and model links below the app title.
- Added the official Spreadsheet-RL paper citation to the app footer.

## [0.1.0] - 2026-08-16

### Added

- Added a Gradio spreadsheet reasoning interface with system and user prompts.
- Added optional text, CSV, TSV, XLS, and XLSX file context.
- Added selectable GGUF quantizations for Spreadsheet-RL-4B with direct llama.cpp inference.
- Added Hugging Face ZeroGPU execution and model preloading support.
- Added final-answer-only response handling for the model's reasoning output.
- Added a Gradio MCP server for programmatic access to inference.
