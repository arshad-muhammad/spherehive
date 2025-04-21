# Employee QR Code Generator

A web application that generates beautiful QR codes for employee ID cards with embedded logos. When scanned, the QR code displays employee details in a beautiful popup format.

## Features

- Upload Excel file with employee details
- Generate QR codes with embedded company logo
- Beautiful web interface for displaying employee details
- Responsive design that works on all devices
- Secure data handling

## Requirements

- Python 3.7 or higher
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone this repository or download the files
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Place your company logo in the `static` folder as `logo.png`
4. Run the application:
   ```bash
   python qr_generator.py
   ```

## Excel File Format

Create an Excel file (.xlsx) with the following columns:
- name
- designation
- phone
- email
- office_address

Example:
| name | designation | phone | email | office_address |
|------|-------------|-------|-------|----------------|
| John Doe | Software Engineer | +1234567890 | john@example.com | 123 Main St, City |

## Usage

1. Open your web browser and go to `http://localhost:5000`
2. Upload your Excel file containing employee details
3. The application will generate QR codes for each employee
4. QR codes will be saved in the `static/qr_codes` directory
5. When scanned, the QR code will display employee details in a beautiful popup

## Customization

- To change the logo, replace `static/logo.png` with your company logo
- To modify the styling, edit the CSS in `templates/index.html`
- To change the QR code appearance, modify the parameters in `qr_generator.py`

## Security Notes

- The application stores employee data in a JSON file
- QR codes contain employee information in JSON format
- Make sure to secure the server where the application is running

## License

This project is licensed under the MIT License - see the LICENSE file for details. 