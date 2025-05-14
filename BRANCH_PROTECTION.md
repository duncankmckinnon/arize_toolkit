# Branch Protection Rules

This document explains how to set up branch protection rules for this repository. These rules ensure that changes to important branches require reviews from code owners.

## Setting up Branch Protection in GitHub

Follow these steps to set up branch protection rules:

1. Go to the repository on GitHub
2. Click on **Settings** (requires admin access)
3. Select **Branches** from the left sidebar
4. Under "Branch protection rules", click **Add rule**
5. Configure the following settings:

### Branch name pattern
Enter `main` (or any other branch you want to protect)

### Protection settings
- ✅ **Require a pull request before merging**
  - ✅ Require approvals (set to 1 or more)
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners
  - ✅ Require approval of the most recent reviewable push

- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Search for and enable these status checks:
    - `validate` (CODEOWNERS validation)
    - `test` (Test workflow)

- ✅ **Require conversation resolution before merging**

- ✅ **Do not allow bypassing the above settings**

6. Click **Create** or **Save changes**

## Additional Protection

Consider enabling these additional settings:

- ✅ **Allow force pushes** - Disable this option (leave unchecked)
- ✅ **Allow deletions** - Disable this option (leave unchecked)

## Testing Your Setup

After setting up these rules:
1. Create a new branch
2. Make changes to files owned by specific code owners
3. Create a PR
4. Verify that the correct code owners are automatically requested for review
5. Verify that the PR cannot be merged until all required reviews are provided 