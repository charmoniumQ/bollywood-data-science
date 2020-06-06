# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue,
email, or any other method with the owners of this repository before making a change.

Please note we have a code of conduct, please follow it in all your interactions with the project.

## To report an issue or request a feature

1. Read the documentation (working on adding more).
2. File an issue in Github.
  - Explain what you are trying to do and why.
  - Include a [minimal reproducible issue](https://minimalworkingexample.com/).

## To fix an issue or implement a feature

1. Report the issue (see above).
2. Branch off of master.
3. Add a test that fails (should be only failure in `./scripts/test.sh`).
4. Fix the issue!
5. Ensure nothing broke `./scripts/test.sh`
5. Submit a pull request.

I recommend adding `./scripts/test.sh` as a pre-commit hook.
