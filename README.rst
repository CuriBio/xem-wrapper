Steps to create repo:
   - Log in as Curi-Bio-CI
   - Select python-github-template as template
   - Check box that says `include all branches`
   - Set repo to public
   - Publish repo
   - To stop error messages about `master` and `development` branches not sharing any history, clone the repo, checkout development and run `git rebase -i origin/master` then `git push -f`
   - In Actions -> Dev: click Run workflow. Wait until workflow finishes
   - In Settings -> Security & analysis: enable Dependabot security updates
   - In Setting -> Options, under Merge Button:
      - Make sure "automatically delete head branches" is checked
      - Make sure squash merging" is NOT checked
   - In Settings -> Branches:
      - Add Rule with master specified as Branch pattern name
         - check Require pull requests reviews before merging
         - check Dismiss stale pull requests
         - check Require Review from Code Owners
         - check Require status checks before merging
         - Under status checks, check all of the python checks (6 total)
         - check Include administrators
         - check Restrict who can push to matching branches
      - Add Rule with development specified as Branch pattern name
         - repeat master branch steps

.. image:: https://github.com/CuriBio/xem-wrapper/workflows/Dev/badge.svg?branch=development
   :alt: Development Branch Build

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
<<<<<<< HEAD
=======

.. image:: https://codecov.io/gh/CuriBio/xem-wrapper/branch/development/graph/badge.svg
  :target: https://codecov.io/gh/CuriBio/xem-wrapper

>>>>>>> Initial commit
