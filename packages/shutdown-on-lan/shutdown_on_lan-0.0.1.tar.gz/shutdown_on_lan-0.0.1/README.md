# Shutdown On Lan

Shutdown On Lan is a FastAPI application that allows you to remotely shut down the system.

## Why?
It's easy to integrate into existing projects like [UpSnap](https://github.com/seriousm4x/UpSnap)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/shutdown-on-lan.git
    ```
2. Navigate to the project directory:
    ```sh
    cd shutdown-on-lan
    ```
3. Activate the virtual environment:
    ```sh
    poetry shell
    ```
4. Install the required dependencies:
    ```sh
    poetry install
    ```

## Usage

1. Start the application:
    ```sh
    fastapi run main.py
    ```
2. Use `curl` to shut down the computer:
    ```sh
    curl "http://localhost:8000/shutdown"
    ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please contact [yourname@example.com](mailto:yourname@example.com).