
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

## v0.1.3

### Added

* A CHANGELOG.md file.

### Changed

* Travis testing with different versions of Python (3.6, 3.7), torch (1.1, 1.2, 1.3, 1.4), and torchvision (0.3, 0.4, 0.5).

### Fixed

* Bugfix when using `td.discount` with replays coming from vectorized environments (@galatolofederico) 
* env.action_size and env.state_size when the number of vectorized environments is 1. (thanks @galatolofederico)
* Actor-critic integration test being to finicky.
* `cherry.onehot` support for numpy's float and integer types. (thanks @ngoby)
