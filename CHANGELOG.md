# CHANGELOG


## v1.1.1 (2025-02-05)

### Bug Fixes

- **ci**: Adapt workflow for Python Semantic Release v7 -> v9
  ([`59e46c9`](https://github.com/developmentseed/pydantic-ssm-settings/commit/59e46c9c83e5b600038360b0d5ce30475482e2bb))

Python Semantic Release V8 brought changes where releases were no longer pushed to Github/PyPI. As
  such, we need to update our workflows.
  https://python-semantic-release.readthedocs.io/en/latest/migrating_from_v7.html


## v1.1.0 (2025-02-04)

### Bug Fixes

- **test**: Ensure client is mocked
  ([`1c89c0c`](https://github.com/developmentseed/pydantic-ssm-settings/commit/1c89c0c1b1c5f91d57765d6c9930e525acdb68ca))

### Chores

- Rename AwsSsmSourceConfig to AwsSsmBaseSettings
  ([`8ea89bb`](https://github.com/developmentseed/pydantic-ssm-settings/commit/8ea89bb6029bf3e09aa3f759682bcece9dd0f8bf))

- Rename classes for brevity
  ([`333ebf6`](https://github.com/developmentseed/pydantic-ssm-settings/commit/333ebf6ea1abd3039bcce9b40995780564a7b30c))

- Rm unused subclassed methods
  ([`af76030`](https://github.com/developmentseed/pydantic-ssm-settings/commit/af76030ad1fd418423d626021cbe8d2771b84a44))

- Up pkg version in lock
  ([`4186d7e`](https://github.com/developmentseed/pydantic-ssm-settings/commit/4186d7e65d47b33f5af3d6f8c91873c3ad79fef5))

- **docs**: Improve readme
  ([`46c5357`](https://github.com/developmentseed/pydantic-ssm-settings/commit/46c53579be48185c0ecee64bdd3dd6f016ef74d1))

- **test**: Rm unused variables
  ([`9b495c6`](https://github.com/developmentseed/pydantic-ssm-settings/commit/9b495c62d17e0d8bec9536f6714e6dd69ec86b22))

### Features

- Support custom boto3 client
  ([`1def3c3`](https://github.com/developmentseed/pydantic-ssm-settings/commit/1def3c32bcde4b12c5951fc2db467ef0cedd9eb0))


## v1.0.0 (2025-02-04)

### Bug Fixes

- Correct python version
  ([`2bd8500`](https://github.com/developmentseed/pydantic-ssm-settings/commit/2bd850018f9642cd621c2422df921f43a4192db2))

- **ci**: Add pytest-cov req
  ([`2dbce3a`](https://github.com/developmentseed/pydantic-ssm-settings/commit/2dbce3aa3821cb995de94e3e55311440c5befaf5))

- **ci**: Set version toml to tuple
  ([`b2cb5ce`](https://github.com/developmentseed/pydantic-ssm-settings/commit/b2cb5ce44a9899657c7cfdc6cd21fc94e33bf5fa))

- **ci**: Set version_variables
  ([`3f1cb70`](https://github.com/developmentseed/pydantic-ssm-settings/commit/3f1cb70f8ba98905ed95385fba9272db8990a617))

- **ci**: Use string
  ([`57167a7`](https://github.com/developmentseed/pydantic-ssm-settings/commit/57167a764a186d1f652aa7ffb3d690696b0c414d))

CI was confusing 3.10 for 3.1

### Chores

- Add python-semantic-release for local dev
  ([`aa0c65f`](https://github.com/developmentseed/pydantic-ssm-settings/commit/aa0c65ff3c449efed159d79063f254e4cc5379e1))

- Improve vscode integration
  ([`25fd6e3`](https://github.com/developmentseed/pydantic-ssm-settings/commit/25fd6e3bd9784af621f475d981013536aa299896))

- Reduce python requirement
  ([`295e0db`](https://github.com/developmentseed/pydantic-ssm-settings/commit/295e0db3a3c17bea3881ec4d0268ea9fd07e7be9))

- Replace poetry with uv
  ([`a916706`](https://github.com/developmentseed/pydantic-ssm-settings/commit/a91670693992719aeadb2f206e192b0c293f4738))

- Typing / docstring cleanup
  ([`92308e3`](https://github.com/developmentseed/pydantic-ssm-settings/commit/92308e38a20b6c1174381d0b33dc01248036ed5f))

- Update upload-artifact action
  ([`91a88ef`](https://github.com/developmentseed/pydantic-ssm-settings/commit/91a88efdf48f0e8ff6ce72132dcf7e3466d01bb4))

- **ci**: Fix lint step
  ([`78f27e4`](https://github.com/developmentseed/pydantic-ssm-settings/commit/78f27e4de8473413c96359019a3532b8cada941d))

- **ci**: Update semantic release step
  ([`30b4e9b`](https://github.com/developmentseed/pydantic-ssm-settings/commit/30b4e9bfc87fcbaa29711db00f979fb95eed8b12))

- **test**: Update ssm mocking
  ([`5b57ca0`](https://github.com/developmentseed/pydantic-ssm-settings/commit/5b57ca0ad2fcedf7e05db7bcde4f3b9288d7037f))

### Continuous Integration

- Install required package
  ([`c1f42ca`](https://github.com/developmentseed/pydantic-ssm-settings/commit/c1f42cab80d71c4c2481f1536acc42dfeb06de66))

### Features

- Adapt to pydantic 2.0 ([#15](https://github.com/developmentseed/pydantic-ssm-settings/pull/15),
  [`420f63d`](https://github.com/developmentseed/pydantic-ssm-settings/commit/420f63d7ae1df1f20429d1052de6c5aef2ecf2ee))

* feat: update to align with pydantic 2.0 and remove dependency on secret file to setup an ssm
  prefix

BREAKING CHANGE: file secrets dir is no longer used to define the ssm prefix

* Fixup

---------

Co-authored-by: Anthony Lukach <anthonylukach@gmail.com>

### BREAKING CHANGES

- File secrets dir is no longer used to define the ssm prefix


## v0.2.4 (2022-09-26)

### Bug Fixes

- Handle extra SSM parameters
  ([#11](https://github.com/developmentseed/pydantic-ssm-settings/pull/11),
  [`4b436de`](https://github.com/developmentseed/pydantic-ssm-settings/commit/4b436de1f2ed5eaef5ec91872b68b34c351ea909))

* bugfix: handle extra SSM parameters

Avoid issues of `extra fields not permitted (type=value_error.extra)` when there are non-relevant
  params stored in SSM.

* Fixes

* Fix

* Flake8 fix

* Flake8 fix again

* Cleanup docs


## v0.2.3 (2022-06-22)

### Bug Fixes

- **security**: Bump pywin32 from 227 to 301
  ([#10](https://github.com/developmentseed/pydantic-ssm-settings/pull/10),
  [`88bc1bd`](https://github.com/developmentseed/pydantic-ssm-settings/commit/88bc1bd3c52fd14e4dfa39d6e8d54e1e7073ad50))

* Bump pywin32 from 227 to 301

Bumps [pywin32](https://github.com/mhammond/pywin32) from 227 to 301. - [Release
  notes](https://github.com/mhammond/pywin32/releases) -
  [Changelog](https://github.com/mhammond/pywin32/blob/main/CHANGES.txt) -
  [Commits](https://github.com/mhammond/pywin32/commits)

--- updated-dependencies: - dependency-name: pywin32 dependency-type: indirect

...

Signed-off-by: dependabot[bot] <support@github.com>

* fix: Bump pywin32 from 227 to 301

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: Anthony Lukach <anthonylukach@gmail.com>

### Chores

- Reformat pyproject.toml
  ([`2a7376b`](https://github.com/developmentseed/pydantic-ssm-settings/commit/2a7376be3efb5644f165bdedb2be658f40666761))


## v0.2.2 (2022-06-21)

### Bug Fixes

- Instruct semantic-releases to up version in poetry config
  ([`650554d`](https://github.com/developmentseed/pydantic-ssm-settings/commit/650554df56e479d64039418a0738d80901b19432))

### Chores

- Add coverage output
  ([`c1c8705`](https://github.com/developmentseed/pydantic-ssm-settings/commit/c1c8705510b3f8008c32f66a440757dd41b03916))


## v0.2.1 (2022-06-21)

### Bug Fixes

- Fix semantic release build command
  ([`13ce3c7`](https://github.com/developmentseed/pydantic-ssm-settings/commit/13ce3c7106d180c44a51462cdab497391afa21ea))


## v0.2.0 (2022-06-21)

### Chores

- Rollback python-semantic-release
  ([`f7115de`](https://github.com/developmentseed/pydantic-ssm-settings/commit/f7115de92dadb187b67f5754bc6109061e15ff00))

https://github.com/relekang/python-semantic-release/issues/450

### Features

- Test auto-versioning
  ([`ab98524`](https://github.com/developmentseed/pydantic-ssm-settings/commit/ab98524d205d0b6567f2221b6804238cbab87568))


## v0.1.0 (2022-06-20)


## v0.0.1 (2022-06-09)
