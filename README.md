<p align="center">
  <img src="./desktop_app/resources/icons/app_icon.png" alt="NexusWare Icon" width="200" height="200">
</p>
<p align="center">
  <b><span style="font-size:24px;">NexusWare</span></b>
</p>

<p align="center">
  <span style="font-size:18px;">Advanced Warehouse Management System</span>
</p>



NexusWare is a cutting-edge, multi-platform Warehouse Management System designed to revolutionize inventory control,
order fulfillment, and warehouse operations. Built with Python and SQLite, NexusWare offers seamless integration
across mobile, web, and desktop environments.

> Although initial development idea was to use Flet lib, it was decided to split the project into separate projects
> for each platform.

<details>
<summary>Feature roadmap</summary>

| Feature                     | Mobile | Web | Desktop |
|-----------------------------|--------|-----|---------|
| User Authentication         | ✅      | ✅   | ✅       |
| Inventory Management        | ✅      | ✅   | ✅       |
| Barcode/QR Scanning         | ✅      | -   | -       |
| Picking and Packing         | ✅      | ✅   | ✅       |
| Receiving                   | ✅      | ✅   | ✅       |
| Shipping                    | ✅      | ✅   | ✅       |
| Cycle Counting              | ✅      | ✅   | ✅       |
| Asset Tracking              | ✅      | ✅   | ✅       |
| Task Management             | ✅      | ✅   | ✅       |
| Real-time Communication     | ✅      | ✅   | ✅       |
| Offline Mode                | ✅      | -   | ✅       |
| Voice Control               | ✅      | -   | -       |
| Augmented Reality           | ✅      | -   | -       |
| Dashboard & Analytics       | -      | ✅   | ✅       |
| Order Management            | -      | ✅   | ✅       |
| Warehouse Layout            | -      | ✅   | ✅       |
| Labor Management            | -      | ✅   | ✅       |
| Supplier Management         | -      | ✅   | ✅       |
| Customer Management         | -      | ✅   | ✅       |
| Integration Hub             | -      | ✅   | ✅       |
| Document Management         | -      | ✅   | ✅       |
| Quality Control             | -      | ✅   | ✅       |
| Billing and Invoicing       | -      | ✅   | ✅       |
| Yard Management             | -      | ✅   | ✅       |
| System Administration       | -      | ✅   | ✅       |
| Offline Database Management | -      | -   | ✅       |
| Advanced Reporting          | -      | -   | ✅       |
| Inventory Planning          | -      | -   | ✅       |
| 3D Warehouse Visualization  | -      | -   | ✅       |
| Barcode and Label Design    | -      | -   | ✅       |
| Advanced Search and Filter  | -      | ✅   | ✅       |
| System Diagnostics          | -      | -   | ✅       |
| Training Mode               | -      | -   | ✅       |
| Customization Tools         | -      | -   | ✅       |

</details>

## Technology Stack

- **Backend:** ✅
  - Python (FastAPI)
  - SQLite
  - Docker

- **Desktop App:** ✅
  - Python
  - Qt Framework (PySide6)
  - SQLite (local database)

- **Mobile App:** TBD/TBA

- **Web Interface:** TBD/TBA

## Architecture

For a detailed description of the system architecture, please refer to the [ARCHITECTURE.md](docs/ARCHITECTURE.md) file.

## Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose

<details>
<summary>How to start?</summary>

1. Clone the repository:
```bash
git clone https://github.com/HardMax71/NexusWare.git
cd NexusWare
```

2. Start the server using Docker Compose:

```bash
docker-compose up --build
```

3. For desktop app:

```bash
# Create and activate virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Navigate to desktop app directory
cd desktop_app

# Install requirements
pip install -r requirements.txt

# Run the application
python main.py

# To deactivate virtual environment when done
deactivate
```

>![NOTE]
> Creds for admin user are:
> - **E-Mail:** admin@example.com
> - **Password:** admin

</details>

## Contributing

We welcome contributions to NexusWare! Please refer to our [CONTRIBUTING.md](docs/CONTRIBUTING.md) file for guidelines
on how to report issues, submit pull requests, and more.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
