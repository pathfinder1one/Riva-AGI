# How a User Provides Access to Environment Variables in a Development Setup

There are several common, well-established ways a user can provide access to environment variables during development. Below is a practical guide covering the most widely used approaches, how they work, and best practices.

---

## 1. `.env` Files (Most Common in Development)

A `.env` file is a plain-text file at the project root that defines key–value pairs. A loader library reads it into the process environment at startup.

**Example `.env` file:**
```bash
DATABASE_URL=postgres://user:pass@localhost:5432/mydb
API_KEY=sk_test_abc123
DEBUG=true
```

**How it's loaded:**

- **Node.js / JavaScript:** the `dotenv` package
  ```js
  require('dotenv').config();   // reads .env → process.env
  ```
- **Python:** `python-dotenv`
  ```python
  from dotenv import load_dotenv
  load_dotenv()                 # reads .env → os.environ
  ```
- **Rust:** the `dotenv` crate
  ```rust
  dotenv::dotenv().ok();
  ```
- **Go:** `godotenv`
  ```go
  godotenv.Load()
  ```

**Key rules:**
- Add `.env` to `.gitignore` so secrets are never committed.
- Provide a `.env.example` (or `.env.template`) with placeholder values so teammates know which variables are required.

---

## 2. Exporting in the Shell

For quick, one-off runs, a user can export variables directly in their terminal session:

```bash
export API_KEY="sk_test_abc123"
export DEBUG=true
./my-app
```

or inline for a single command:

```bash
API_KEY="sk_test_abc123" node server.js
```

These variables live only in that shell session and are inherited by child processes.

---

## 3. Shell Configuration Files (Persistent Per-User)

Users can persist variables across sessions in shell profile files:

- **Bash:** `~/.bashrc` or `~/.bash_profile`
- **Zsh:** `~/.zshrc`
- **Fish:** `~/.config/fish/config.fish`

```bash
# ~/.zshrc
export DATABASE_URL="postgres://user:pass@localhost:5432/mydb"
```

> ⚠️ **Caution:** Avoid putting real secrets in these files if they're synced or shared. Prefer `.env` + a secrets manager.

---

## 4. OS / IDE Native Mechanisms

- **macOS:** `launchctl setenv KEY value` (for GUI apps)