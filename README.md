# 🧪 Rotor Management System

> A simple and intuitive web-based application for managing laboratory inventories (solid-state NMR rotors) integrated with eLabFTW.

---

## ✨ Features

- 📊 **Dashboard** - View all rotors at a glance
- 🔄 **Update Rotor** - Modify rotor status and information
- 🔍 **Search & Filter** - Find rotors by owner or other criteria  
- 📜 **History Tracking** - See past updates and modifications
- 🗂️ **Global Logs** - Track all system changes

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/) package manager
- eLabFTW account and API access

### Installation

```bash
# Clone the repository
git clone https://github.com/yufewu/rotor_management_elabftw.git
cd rotor_management_elabftw

# Install dependencies (uv will handle virtual environment automatically)
uv sync
```

### Configuration

1. Create `.streamlit/secrets.toml` (or use Streamlit Cloud secrets):
```toml
[elab]
API_KEY = "<your_elab_api_key>"
API_HOST = "https://<your-elab-instance-url>/api/v2"
CATEGORY_ID = "<id of the resource template>"
```

### Run the Application

```bash
uv run streamlit run Rotor_catalogue.py
```

The app will open at `http://localhost:8501`, as well as an ip adress accessible within your local (institute) network. 

---

## 🏗️ Project Structure

```
rotor_management_elabftw/
├── Rotor_catalogue.py           # Main page
├── pages/                 # Sub-pages
│   ├── Update.py
│   └── Search_rotor_history.py
├── api_services/          # API integration
│   └── client.py
│   └── rotor_manager.py
│   └── types.py
├── utils/                 # Helper functions
│   └── data_parser.py
│   └── supporting_data.py
├── .streamlit/                 # Helper functions
│   └── secrets.toml
└── pyproject.toml
└── README.md
```

---

## 📚 Tech Stack

- **Frontend**: Streamlit
- **Backend**: eLabFTW API
- **Data Processing**: Python, Pandas
- **Language**: Python 3.11+

---


## 👨‍💻 Author

- **Yufe Wu** - yufei.wu AT cec DOT mpg DOT de

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Last Updated**: March 2026
---
