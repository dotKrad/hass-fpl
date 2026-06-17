# Contribution guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Github is used for everything

Github is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `master`.
2. If you've changed something, update the documentation.
3. Make sure your code lints (using black).
4. Issue that pull request!

## Releases

This project uses [Release Please](https://github.com/googleapis/release-please) to automate versioning and GitHub releases for HACS update notifications.

1. Use [Conventional Commits](https://www.conventionalcommits.org/) in **squash merge** PR titles:
   - `fix: ...` → patch release (e.g. 1.0.0 → 1.0.1)
   - `feat: ...` → minor release (e.g. 1.0.0 → 1.1.0)
   - `feat!: ...` or `BREAKING CHANGE:` in the body → major release
2. After merges to `master`, Release Please opens a **Release PR** that bumps `custom_components/fpl/manifest.json` and updates `CHANGELOG.md`.
3. **Merge the Release PR** — Release Please creates the GitHub release and tag (e.g. `v1.1.0`). HACS detects the new version and notifies users.

To force a specific version (e.g. first release after adopting Release Please), add `Release-As: 1.1.0` to a commit message body.

Repository setting required: **Settings → Actions → General → Allow GitHub Actions to create and approve pull requests**.

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](../../issues)

GitHub issues are used to track public bugs.  
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

Use [black](https://github.com/ambv/black) to make sure the code follows the style.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
