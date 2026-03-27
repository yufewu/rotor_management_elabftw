# 📝 Rotor Inventory & Status Management System

*(Based on eLabFTW + Streamlit)*

---

## 1. Project Overview

This project aims to develop a web-based inventory management system for tracking and managing laboratory rotors. The system leverages the existing **eLabFTW** platform as the backend database and interacts with it via its API for data operations. A modern, user-friendly interface is built using **Streamlit**.

The primary objective is to provide a lightweight, efficient, and transparent solution for managing rotor usage, ownership, and history within a lab environment.

---

## 2. Core Features

The system consists of five key modules implemented within a Streamlit multipage application:

### 1. Dashboard (Global Overview)

* Displays all rotors in a tabular format
* Shows real-time status and metadata (Rotor number, Owner, Status, Sample name, etc.)

### 2. Update Rotor

* Provides a form-based interface
* Allows users to modify rotor attributes by entering a rotor number
* Sends updates to eLabFTW via API (`PATCH` request)

### 3. Search by Owner

* Enables filtering rotors by owner name
* Displays all rotors currently assigned to a specific user

### 4. Rotor History

* Retrieves historical records for a specific rotor
* Tracks past usage and ownership changes

### 5. Global Logs

* Displays all modification records across the system
* Includes details such as:

  * Who made the change
  * When the change occurred
  * What was modified

---

## 3. System Architecture

To ensure performance and reduce API load on eLabFTW, the system adopts a **hybrid storage architecture**:

### Frontend

* Streamlit multipage application

### Backend

* **Primary Database**: eLabFTW

  * Stores the **current state** of each rotor
  * Uses the *Items (Resources)* module

* **Logging Database**: Local storage (SQLite or CSV)

  * Stores **historical modification records**
  * Implements a **dual-write strategy**:

    * Each update triggers:

      1. API call to eLabFTW
      2. Local log entry

---

## 4. Data Model

Each rotor corresponds to an individual **Item (Resource)** in eLabFTW.

Core business data is stored in the `metadata` field (JSON format).
Special care is required for handling **double JSON serialization**.

### Extracted Fields:

* `Rotor number` — Unique identifier
* `Status` — Current state (e.g., Idle, In Use)
* `Owner` — Current user
* `Sample name` — Associated sample
* `Date` — Operation date
* `Location` — Storage location
* `Note` — Additional remarks

---

## 5. Development Roadmap

### Phase 1: Foundation

* [x] Initialize Python virtual environment
* [x] Install dependencies (`streamlit`, `elabapi-python`, `pandas`)
* [x] Set up project structure:

  * `pages/`, `api_services/`, `utils/`, `db/`
* [x] Implement API client (`client.py`)
* [x] Build robust data parser (`data_parser.py`)

  * Handles `NoneType` and nested JSON issues

---

### Phase 2: Read-Only UI

* [x] Implement rotor retrieval (`get_all_rotors()`)
* [x] Build Dashboard page
* [x] Implement Search by Owner functionality

---

### Phase 3: Write Operations

* [x] Implement rotor update API (`update_rotor`)
* [x] Build update form using `st.form`
* [x] Integration testing with eLabFTW

---

### Phase 4: Logging & History *(In Progress)*

* [x] Implement logging utility (`history_logger.py`)
* [x] Extend update workflow with logging hook
* [x] Build Global Logs page
* [x] Build Rotor History page

---

## 6. Key Challenges & Considerations

### 1. Data Integrity

* eLabFTW allows manual edits → potential inconsistent data
* Use defensive parsing:

  ```python
  data.get("key", "default_value")
  ```
* Prevent frontend crashes due to missing fields

### 2. Performance & Latency

* Fetching all items on each load can be slow
* Recommended optimization:

  ```python
  @st.cache_data(ttl=60)
  ```
* Cache data for 60 seconds to reduce API calls

### 3. Concurrency Conflicts

* No strict locking mechanism implemented
* Conflict resolution strategy:
  **Last write wins**

---

## 7. Tech Stack

* **Frontend**: Streamlit
* **Backend API**: eLabFTW API
* **Data Processing**: Pandas
* **Local Storage**: SQLite / CSV
* **Language**: Python

---

## 8. Future Improvements

* Add user authentication and role-based access control
* Implement real-time updates (WebSocket or polling)
* Introduce conflict detection mechanisms
* Improve UI/UX with better filtering and visualization
* Add export functionality (CSV / Excel reports)

---

## 9. Getting Started (Quick Guide)

1. Clone the repository
2. Create a virtual environment
3. Install dependencies:

   ```
   git clone https://github.com/yufewu/rotor_management_elabftw.git
   cd rotor_management_elabftw
   uv sync
   ```
4. Configure eLabFTW API credentials
5. Run the application:

   ```
   uv run streamlit run dashboard.py
   ```

---

## 10. License

This project is distributed under MIT license. 
