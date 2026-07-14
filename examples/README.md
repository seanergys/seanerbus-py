<!--
SPDX-FileCopyrightText: 2026 SEANERGYS Partners <https://seanergys.eu>

SPDX-License-Identifier: MIT
-->

# Python examples for the SeanerBUS

These are the Python examples for the SeanerBUS.

## Setup

From the **seanerbus root directory**, create a virtual environment and install the Python package:

```sh
uv venv .venv
source .venv/bin/activate
uv pip install bindings/python/
```

## Running the examples

With the server running (`cd server && cargo run`) and the virtual environment activated:

```sh
# Publish/subscribe test — two shells:
python3 python_examples/src/publish_test.py   a366335b-52f0-4658-a42b-7e73e83ec91f
python3 python_examples/src/subscribe_test.py a366335b-52f0-4658-a42b-7e73e83ec91f

# Request/response test — two shells:
python3 python_examples/src/response_test.py  a366335b-52f0-4658-a42b-7e73e83ec91f
python3 python_examples/src/request_test.py   a366335b-52f0-4658-a42b-7e73e83ec91f
```

Replace the UUID with one of your own choosing, or use the same UUID shown above.
Any combination of Python, Rust, and C++ examples interoperates.
