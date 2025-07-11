# URL Shortener Project - DubLynk

## Overview

DubLynk allows both registered and unregistered users to create shortened versions of URLs and QR codes. For registered users, additional features include the ability to generate custom URLs, track visits on both custom and non-custom URLs, and view the history of generated short URLs.

## Features

- **URL Shortening:**
  - Both registered and unregistered users can create shortened URLs.
  - Registered users can generate custom URLs and track visits on all URLs.
  - Both registered and unregistered users can generate QR codes for Shortened URLS.

- **Analytics:**
  - The system automatically tracks the number of visits to each shortened URL.
  - Registered users can view analytics and the history of generated short URLs.

## Getting Started

### Prerequisites

- Python 3.x
- MySQL database

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Orjihenry/url-shortener.git
    ```

2. Install dependencies:

    ```bash
    cd url-shortener
    pip install -r requirements.txt
    ```

3. Set up the database:

    - Create a MySQL database named `url_shortener`.
    - Copy config_example.py to a new file named config.py.
    - Replace placeholder values in config.py with actual config values,
      such as database credentials and secret keys.

4. Run the application:

    ```bash
    python main.py
    ```

5. Open your web browser and visit [http://localhost:5000](http://localhost:5000).

## Usage

1. **Registration:** Users can register for an account.

2. **Login:** Once registered, users can log in using their credentials.

3. **URL Shortening:**
    - After logging in, users can visit the dashboard to shorten a new URL.
    - They can input the long URL, and a shortened version will be generated.

4. **Analytics:**
    - The system automatically tracks the number of visits to each shortened URL.
    - Registered users can view analytics and the history of generated short URLs.

## User Access

- **All Users:**
  - Can create shortened URLs.

- **Registered Users:**
  - Can generate custom URLs.
  - Can track visits on all URLs.
  - Can view the history of generated short URLs.

## GitHub Issues

Please adhere to the following guidelines when using GitHub Issues:

1. **Bug Reports:** Open an issue only for actual bugs.

2. **Questions/Ideas:** Use GitHub Discussions for questions, ideas, or general items.

3. **Avoiding Noise:** This policy prevents bugs from being drowned out by enhancement suggestions or help requests.

## Contributing

Contributions are welcome! If you have any improvements or features, please submit a pull request.

  - **Branch Naming:** Name your branch 'bug-fix' or 'features' to make corrections or add new features.
  - **Pull Requests**: Submit a pull request detailing the change(s) you made.

Happy Hacking!
