# SDK alpha reproducible artifact candidate

## Objective

Prepare reproducible, inspectable wheel evidence for the unreleased standalone
`projectkoios-workflow-sdk==0.1.0a1` without publishing, uploading, tagging,
releasing, changing a version, or designating an archive as canonical.

This task evaluates artifact construction and owner compatibility only. It does
not accept a public compatibility policy, release channel, production use,
complete Task/Workflow API, full Workflow runtime distribution, or worker
isolation.

## Historical candidate: exact source and builder

The candidate was built from two independent public clones checked out at exact
revision:

`fe600fa1b857cd030832b226a8e21e0a30f4f1b6`

Only the `sdk/` build project was built. Each clone was clean and its resolved
`HEAD` was asserted before construction. The fixed build inputs were:

| Input | Exact value |
| --- | --- |
| `SOURCE_DATE_EPOCH` | `1792155504` |
| Python | `3.14.6` |
| `build` | `1.6.1` |
| `setuptools` | `84.0.0` |
| `packaging` | `26.3` |
| `pyproject-hooks` | `1.3.3` |
| `PYTHONHASHSEED` | `0` |
| locale | `C` |

The two builds used the same dedicated build environment but distinct clean
source clones and output directories. `SOURCE_DATE_EPOCH` is the exact source
commit time. Build isolation was disabled only after installing the exact
builder versions above; `sdk/pyproject.toml` itself pins
`setuptools==84.0.0`.

The normalized procedure, repeated for `source-a` and `source-b`, was:

```text
git clone --no-checkout https://github.com/eragasa/projectkoios-workflow.git SOURCE
git -C SOURCE checkout fe600fa1b857cd030832b226a8e21e0a30f4f1b6
test "$(git -C SOURCE rev-parse HEAD)" = \
  fe600fa1b857cd030832b226a8e21e0a30f4f1b6
python3.14 -m venv BUILD_ENV
PIP_CONFIG_FILE=/dev/null BUILD_ENV/bin/python -m pip install \
  build==1.6.1 setuptools==84.0.0 packaging==26.3 pyproject-hooks==1.3.3
SOURCE_DATE_EPOCH=1792155504 PYTHONHASHSEED=0 LC_ALL=C \
  BUILD_ENV/bin/python -m build --wheel --no-isolation \
  --outdir OUTPUT SOURCE/sdk
```

## Historical candidate: reproducible result

Both builds produced byte-identical archives:

| Property | Value |
| --- | --- |
| Filename | `projectkoios_workflow_sdk-0.1.0a1-py3-none-any.whl` |
| SHA-256 | `7696e45a0de0cc99c9a4e8c577bc4991ea51dd5636151f56ab4e055277580dfd` |
| Size | 17,786 bytes |
| ZIP entries | 12 |
| Wheel tag | `py3-none-any` |
| Purelib | true |

Every ZIP entry has the timestamp selected by `SOURCE_DATE_EPOCH`. The result is
local two-build reproducibility evidence, not yet cross-operating-system release
reproducibility.

## Historical candidate: source and `RECORD` verification

The wheel contains exactly the eight expected SDK package files and four
`.dist-info` files. Every package file is byte-identical to source at the exact
revision:

| Package file | Bytes | SHA-256 |
| --- | ---: | --- |
| `__init__.py` | 218 | `46132bae347e178a4dc4e4d0efe9717551da2d7f1679be43eddd646bc9582d0a` |
| `_validation.py` | 6,895 | `38e394e7169bb9ec0ac77989b10100c1f3c86ed05655bced30e88bebf0af2e3b` |
| `firing.py` | 24,891 | `791102e7f8b122826281ae5990ba016bb1fceee956f26ddedc0ed226f1f75e2a` |
| `identities.py` | 3,904 | `32500383d7b255d5051921d6fda3a01bf7e5329e7693e6d2ef63adf9200f6eb1` |
| `integration.py` | 3,919 | `40b7ec2aa81873656b2590df399204987a60f590d1741e824170c91d5c17e257` |
| `payloads.py` | 4,359 | `54858c4c05a207808855a170812c134f958d535641ffbdcd5a07782ead411abd` |
| `py.typed` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `serialization.py` | 30,312 | `ac2f2b1c156c040f0aff49778363bac825e8f959e67e00bd716eb39a1189dac1` |

All non-`RECORD` rows were independently checked against their URL-safe Base64
SHA-256 and exact byte length. The `RECORD` row itself has the required empty
digest and size. No unexpected or duplicate archive member exists.

Metadata verification found:

- name `projectkoios-workflow-sdk`;
- version `0.1.0a1`;
- `Requires-Python: >=3.14`;
- `License-Expression: Apache-2.0`;
- no runtime `Requires-Dist` dependency; and
- `pytest`, Ruff, MyPy, and `build` only behind the `dev` extra.

## Relationship to earlier wheels

The retained authorized historical wheel has SHA-256:

`925f6974c49c8935ebf2f002b18c86d29375e1b11c3ffc17a29d305fb8095ff4`

Every ZIP entry in that retained wheel is byte-identical to the corresponding
entry in the reproducible candidate, including `METADATA`, `WHEEL`, and
`RECORD`. The archives themselves are not byte-identical because their ZIP
container metadata differs. The retained archive identity remains valid
historical evidence and is not replaced by the candidate.

Pull-request CI has also produced transient archive identities, including
`9862adeb...`, `0f19f17d...`, and other local CI simulations, because those
builds intentionally proved exact source consumption without fixing a canonical
wheel epoch. Source parity must not be represented as archive identity.

## Historical candidate: clean installation and compatibility

A fresh Python 3.14 environment installed only the candidate wheel. It retained
only `pip` and `projectkoios-workflow-sdk`, passed `pip check`, and imported the
SDK under `python -I`. The installed version was exactly `0.1.0a1`, and the
installed metadata exposed no runtime dependency.

A separate clean environment installed the candidate and `pytest==9.1.1`; all
standalone SDK tests passed:

```text
13 passed
pip check: no broken requirements
```

A fresh Simulations environment then installed the exact candidate wheel and
`projectkoios-simulations@4f05789d63f4cb2851c1e4f0ee0d6666e1875a67`
with `.[development]` in one resolver invocation:

```text
696 passed, 8 skipped, 202 subtests passed
pip check: no broken requirements
```

After explicitly composing the optional full Workflow runtime wheel built from
rollback baseline `ee581b5c148adb0c678046ecfb50de0fad72da30` (wheel SHA-256
`e5152762a923e0618508bdde419b79b16cf6023e237a989edea0baa0024aa89e`),
the real-owner runtime-coupled test and complete suite passed:

```text
QE runtime-coupled test: 2 passed
complete composed suite: 698 passed, 7 skipped, 202 subtests passed
pip check: no broken requirements
```

Public Git and package-index retrieval were used for source and declared test
dependencies. No QE executable, calculator, scheduler, effect, owner network
provider, release, or artifact upload was invoked.

## License-corrected reproducible candidate

The correction was committed at exact revision:

`a103687d472ff37d367c150ef565b01d4df23e4a`

Two independent clean local clones were detached at that revision and asserted
clean before building only `sdk/`. Public-clone retrieval remains pending until
the commit is pushed. The fixed build inputs matched the historical build except
for the source-derived epoch:

| Input | Exact value |
| --- | --- |
| `SOURCE_DATE_EPOCH` | `1792207647` |
| Python | `3.14.6` |
| `build` | `1.6.1` |
| `setuptools` | `84.0.0` |
| `packaging` | `26.3` |
| `pyproject-hooks` | `1.3.3` |
| `PYTHONHASHSEED` | `0` |
| locale | `C` |
| timezone | `UTC` |

Both builds produced this byte-identical wheel:

| Property | Value |
| --- | --- |
| Filename | `projectkoios_workflow_sdk-0.1.0a1-py3-none-any.whl` |
| SHA-256 | `49d6bf1aa4c1fa32ae2385f800d2146af90f70e9d58412e5ce71a2b9e0b7de50` |
| Size | 22,006 bytes |
| ZIP entries | 13 unique entries |
| Wheel tag | `py3-none-any` |
| Purelib | true |

Exact inspection proved:

- all eight package files are byte-identical to source at the committed
  revision;
- exactly one license member exists at
  `projectkoios_workflow_sdk-0.1.0a1.dist-info/licenses/LICENSE`;
- that member is 11,357 bytes and byte-identical to both `sdk/LICENSE` and the
  repository-root `LICENSE`;
- its SHA-256 is
  `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`;
- the remaining four members are `METADATA`, `WHEEL`, `top_level.txt`, and
  `RECORD`;
- every non-`RECORD` row has the correct URL-safe Base64 SHA-256 and byte
  length, while the `RECORD` self-row has empty digest and size;
- no unexpected or duplicate member exists; and
- metadata retains version `0.1.0a1`, Python `>=3.14`,
  `License-Expression: Apache-2.0`, no runtime dependency, and development-only
  test and build requirements.

A fresh candidate-only environment passed `pip check` and imported version
`0.1.0a1` under `python -I`. A separate installed-wheel environment passed:

```text
standalone SDK tests: 14 passed
pip check: no broken requirements
```

A fresh environment installed the exact corrected wheel and
`projectkoios-simulations@4f05789d63f4cb2851c1e4f0ee0d6666e1875a67`
with `.[development]` in one resolver invocation:

```text
base suite: 696 passed, 8 skipped, 202 subtests passed
pip check: no broken requirements
```

The optional full Workflow runtime wheel was then built from the same exact
Workflow revision. Its SHA-256 was
`049f706993b63b12cea2a2cb101546f55f591e6b4af67bf9f3ac53d75da68752`.
After explicitly installing that wheel, compatibility remained intact:

```text
QE runtime-coupled test: 2 passed
complete composed suite: 698 passed, 7 skipped, 202 subtests passed
pip check: no broken requirements
```

No QE executable, calculator, scheduler, effect, owner network provider,
release, tag, or artifact upload was invoked.

## Release-preparation finding

Finding disposition: `NO_ACTION_REQUIRED`

Problem: the historical `925f...` and `7696...` wheels declare
`License-Expression: Apache-2.0` but contain no license text.

Evidence: the corrected exact-revision wheel contains one license member with
the exact repository license digest, while its package files, metadata,
`RECORD`, installation, and Simulations compatibility checks all pass.

Consequence: the historical wheels remain non-releasing development evidence
and are not rewritten. Their defect does not carry into the corrected
candidate.

Next action: none for this license finding. Public-source retrieval and CI may
be checked after an authorized push. Canonical-artifact designation, tag,
upload, and release remain separate unauthorized actions.

## Version and channel decision

Finding disposition: `NO_ACTION_REQUIRED`

Public distribution checks on 2026-10-17 found:

- the PyPI JSON endpoint for `projectkoios-workflow-sdk` returned HTTP 404;
- the public Workflow repository had no GitHub releases; and
- the public Workflow repository had no Git tags.

These observations show no discoverable public release. They cannot prove the
absence of a private or otherwise accepted external distribution.

The operator selected the recommended first path: retain `0.1.0a1` for the
license-corrected candidate and classify wheel `925f...` only as historical
development evidence. This resolves the version choice for the non-releasing
candidate; it does not retroactively change any historical archive identity or
authorize a public release.

If contrary evidence later shows that an external consumer treated an earlier
`0.1.0a1` artifact as released, revisit the decision and issue a new alpha
rather than publishing different contents under an accepted version. Keep the
full Workflow runtime experimental and outside this decision.

## Current outcome

Review outcome: `NO_BLOCKING_FINDINGS` for the stated non-releasing artifact
preparation scope.

Operator request: `AUTHORIZATION_REQUIRED` before committing this exact
artifact evidence or pushing the correction and evidence commits. A
canonical-artifact designation, tag, upload, or release remains separately
unauthorized.
