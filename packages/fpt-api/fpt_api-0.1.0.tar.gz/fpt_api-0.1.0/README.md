# fpt-api

A thread-safe wrapper around Flow Production Tracking (formerly ShotGrid) that extends [shotgun_api3](https://github.com/shotgunsoftware/python-api) to support query field retrieval and parallel processing.

## Features

- 🔍 Retrieves query fields (not supported in base `shotgun_api3`)
- 🧵 Thread-safe operations (not supported in base `shotgun_api3`)
- ⚡ Parallel processing for improved performance
- 🔌 Drop-in replacement for basic shotgun_api3 operations

## Installation

From PyPI:

    pip install fpt-api
    pip install git+https://github.com/shotgunsoftware/python-api.git

From source:

    pip install git+https://github.com/ksallee/fpt-api.git
    pip install git+https://github.com/shotgunsoftware/python-api.git

## Why This Wrapper?

The standard `shotgun_api3` library has two main limitations:
1. No support for query field retrieval, which is essential for reporting and analytics
2. Not thread-safe, which can cause issues in multi-threaded applications

This wrapper addresses both issues by:
- Implementing query field retrieval
- Adding thread safety
- Parallelizing query field retrieval for better performance

## Usage

### Basic Usage

    from fpt_api import FPT

    # Initialize the client
    fpt = FPT(
        "https://yourshotgunurl.com",
        script_name="your_script_name",
        api_key="your_script_key"
    )

    # Find a single shot
    shot = fpt.find_one(
        "Shot",
        [["id", "is", 1234]],
        ["code", "sg_status_list", "sg_query_field"]
    )

    # Find multiple shots
    shots = fpt.find(
        "Shot",
        [["id", "in", [1234, 12345]]],
        ["code", "sg_status_list", "sg_query_field"]
    )

### API Reference

Check out the [Official Shotgun API Reference](https://developers.shotgridsoftware.com/python-api/reference.html) for more information on the base `shotgun_api3` library.
FPT does not change the base API, but rather extends it with additional functionality.

## Performance Notes

- Query fields are retrieved in parallel using threads
- Results are returned only after all query fields are retrieved
- Future versions may implement asynchronous retrieval using futures

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.