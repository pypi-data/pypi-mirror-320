# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Test coverage reporting
- Additional example files for demonstration
- Comprehensive documentation in README.md

## [0.2.8] - 2025-01-12
### Added
- Set environment variables `HF_HOME` and `GRADIO_TEMP_DIR`.
- Created directories with appropriate permissions.

### Changed
- Updated input components and settings for summarization.
- Improved error handling and messages.

## [0.2.7] - 2025-01-06

### Added

- Dockerfile for building the Docker image of the gradio_app web application.

### Changed

- Modified `src/summarizer/webapp/gradio_app` to make it accessible from anywhere.

## [0.2.6] - 2025-01-04

### Added

- Added a title "SummaryMaker" to the Gradio interface.

## [0.2.5] - 2025-01-04

### Added

- Added images of Flask and Gradio GUIs to the `README.md` file.

## [0.2.4] - 2025-01-04

### Added

- Added a textarea for the summary output in the Flask web application to better handle longer summaries.

### Fixed

- Ensure the summary result fields are cleared whenever a new input choice is selected.

## [0.2.3] - 2025-01-04

### Fixed

- Ensure the input fields are cleared when a new input choice in the Gradio web application.
- Set the Gradio temporary directory to `~/.gradio_tmp` to avoid permission issues.

## [0.2.2] - 2025-01-04

### Changed

- Set the default input field choice to "Text" in the Gradio web application.
- Ensure the Text field is shown.

## [0.2.1] - 2025-01-03

### Added

- Added Gradio web application interface (`gradio_app.py`).

### Changed

- Updated dependencies in `requirements.txt`.

## [0.2.0] - 2025-01-03

### Added

- Web application interface using Flask
- Ability to summarize text from URLs, files, and direct text input via the web application
- JavaScript-based input type selection for the web application
- Clear previous summary results upon new submission in the web application

### Changed

- Updated version number in `setup.py` to 0.2.0
- Added Flask as a dependency in `requirements.txt`
- Updated `README.md` to reflect the new web application features

## [0.0.3] - 2024-12-31

### Changed

- Updated version number in `setup.py` to 0.0.3
- Specified `numpy<2.0` in `requirements.txt` to avoid compatibility issues

### Fixed

- Resolved NumPy version compatibility issues on Windows

## [0.0.2] - 2024-12-31

### Added

- Added GitHub Actions workflow for publishing to PyPI

## [0.0.1] - 2024-12-29

### Added

- Initial release of the summarizer package
- Core summarization functionality:
  - Text summarization using transformer models
  - Support for T5 and BART model architectures
  - Configurable maximum summary length
  - Adjustable model parameters
- Command-line interface features:
  - File input support with various encodings
  - URL content extraction and summarization
  - Progress bar for long-running operations
  - Colored output for better readability
- Input/Output handling:
  - Multiple text encoding support (UTF-8, ASCII, etc.)
  - Automatic encoding detection
  - Graceful error handling for malformed inputs
- Web content processing:
  - HTML content extraction
  - Automatic main content detection
  - Retry mechanism for failed requests
  - Support for various HTML formats
- Error handling and user feedback:
  - Descriptive error messages
  - Debug mode for detailed logging
  - Input validation
  - Performance warnings for large texts
- Development infrastructure:
  - Basic test suite
  - Project structure setup
  - Development environment configuration
  - Package distribution files

### Changed

- N/A (Initial release)

### Deprecated

- N/A (Initial release)

### Removed

- N/A (Initial release)

### Fixed

- N/A (Initial release)

### Security

- Input validation for URL processing
- Secure handling of file operations
- Rate limiting for web requests
- Timeout handling for external API calls
