<div align="center">
  <img src="./logo.png" alt="kapito Logo" width="100">
  <h1>Kapito</h1>
  <p>A Webpage Analyzer.</p>
  <a href="https://github.com/walidsa3d/actions/workflows/test.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/walidsa3d/kapito/test.yml?branch=main&style=flat-square" alt="Test Status">
  </a>
  <a href="https://github.com/walidsa3d/kapito/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/walidsa3d/kapito?style=flat-square" alt="License">
  </a>
</div>

kapito is a webpage analyzer and technology detector.

## 🚀 Features
- 🧑‍💻 Technology Detection: Automatically detect frameworks, wafs, servers, captchas, libraries, CMS, and other tech stacks (e.g., Django, WordPress, React).
- 📊 Comprehensive Webpage Analysis: Analyze page structure, metadata, and resources.
- 🛠️ CLI and Python API: Simple command-line tool with an intuitive Python API for deeper integrations.
- 🖥️ Performance Metrics: Measure page load times, resource sizes, and other performance factors.
- 📝 Report Generation: Export analysis results as detailed reports in JSON, CSV, or human-readable formats.

## Installation
```bash
pip install kapito
```

## Usage
CLI Example:

Analyze a webpage with the CLI:
```bash

kapito https://example.com
```
Python API Example:
```python

from kapito import Analyzer

analyzer = Analyzer()
report = analyzer.analyze("https://example.com")
print(report)
```

## 🧑‍💻 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License. See the LICENSE file for more details.


