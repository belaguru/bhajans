# Changelog

All notable changes to the Belaguru Bhajans project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-03-22

### Added
- MP3 upload feature (max 5MB, .mp3 only) with file validation
- 5 original chants restored from git history:
  - Om Namah Shivaya
  - Gayatri Mantra
  - Hare Krishna Mahamantra
  - Om Namo Narayanaya
  - Mahamrityunjaya Mantra
- HTML5 audio player on bhajan detail pages with gradient styling
- Database migration script for mp3_file column
- Comprehensive QA reports for all 3 development phases
- Automated testing workflow (pre-commit hooks, nightly E2E tests)

### Changed
- Bhajan model now includes mp3_file field (String 500, nullable)
- Create/edit forms accept file uploads via multipart/form-data
- API endpoints support both JSON and multipart/form-data
- Total bhajan count: 269 → 274 (5 chants restored)

### Technical Details
- Backend validates file size (max 5MB) and extension (.mp3 only)
- Auto-generates unique filenames with timestamp + sanitized title
- Automatically deletes old MP3 files when updating
- Mobile-responsive audio player design
- Client-side file validation for better UX

### Testing
- 56 unit tests passing (100%)
- 31 E2E tests passing (100%)
- QA approved all 3 phases ✅
- Pre-commit hooks prevent broken commits

### Database
- Migration script adds mp3_file column safely
- Backward compatible (existing bhajans unaffected)
- Column defaults to NULL for existing records
