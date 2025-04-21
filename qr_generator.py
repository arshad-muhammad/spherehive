import os
import pandas as pd
import qrcode
from PIL import Image, ImageDraw
from flask import Flask, render_template, jsonify, request, send_file, url_for
import json
from datetime import datetime

app = Flask(__name__)

# Configuration
QR_CODE_DIR = 'static/qr_codes'
EMPLOYEE_DATA_FILE = 'employee_data.json'
LOGO_PATH = 'assets/spherehive logo.jpg'  # Updated logo path
BASE_URL = 'https://spherehive.in'  # Updated to use your domain

# Ensure directories exist
os.makedirs(QR_CODE_DIR, exist_ok=True)

def create_rounded_mask(size, radius):
    """Create a rounded rectangle mask"""
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), size], radius, fill=255)
    return mask

def is_position_marker(x, y, size):
    """Check if the given coordinates are part of a position marker"""
    # Position markers are 7x7 modules in the corners
    marker_size = 7
    # Check if coordinates are in any of the three position markers
    return ((x < marker_size and y < marker_size) or  # Top-left
            (x > size - marker_size and y < marker_size) or  # Top-right
            (x < marker_size and y > size - marker_size))  # Bottom-left

def generate_qr_code(employee_data):
    """Generate QR code with logo for an employee"""
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # Create URL for employee details
    employee_url = f"{BASE_URL}/employee/{employee_data['name']}"
    
    # Add URL to QR code
    qr.add_data(employee_url)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    # Convert to RGBA for color manipulation
    qr_img = qr_img.convert('RGBA')
    data = qr_img.getdata()
    width, height = qr_img.size
    
    # Create new image data with red position markers
    new_data = []
    for y in range(height):
        for x in range(width):
            pixel = data[y * width + x]
            # Change color to red only for position markers
            if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0 and is_position_marker(x, y, width):
                new_data.append((255, 0, 0, 255))  # Red color for position markers
            else:
                new_data.append(pixel)
    
    # Update image with new data
    qr_img.putdata(new_data)
    
    # Add rounded corners to QR code
    mask = create_rounded_mask(qr_img.size, 40)  # 40 is the radius for rounded corners
    qr_img.putalpha(mask)
    
    # Create a new image with white background
    final_img = Image.new('RGBA', qr_img.size, (255, 255, 255, 255))
    final_img.paste(qr_img, (0, 0), qr_img)
    
    # Add logo to QR code
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH)
        # Calculate logo size (25% of QR code size)
        logo_size = int(final_img.size[0] * 0.25)
        logo = logo.resize((logo_size, logo_size))
        
        # Create a circular mask for the logo
        logo_mask = Image.new('L', (logo_size, logo_size), 0)
        draw = ImageDraw.Draw(logo_mask)
        draw.ellipse((0, 0, logo_size, logo_size), fill=255)
        
        # Apply the mask to the logo
        logo.putalpha(logo_mask)
        
        # Calculate position to paste logo
        pos = ((final_img.size[0] - logo.size[0]) // 2,
               (final_img.size[1] - logo.size[1]) // 2)
        
        # Create a white circular background for the logo
        white_bg_size = logo_size + 8
        white_bg = Image.new('RGBA', (white_bg_size, white_bg_size), (255, 255, 255, 255))
        white_bg_mask = Image.new('L', (white_bg_size, white_bg_size), 0)
        draw = ImageDraw.Draw(white_bg_mask)
        draw.ellipse((0, 0, white_bg_size, white_bg_size), fill=255)
        white_bg.putalpha(white_bg_mask)
        
        # Paste white background and logo
        final_img.paste(white_bg, (pos[0] - 4, pos[1] - 4), white_bg)
        final_img.paste(logo, pos, logo)
    
    return final_img

def process_excel_file(file_path):
    """Process Excel file and generate QR codes for each employee"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Convert DataFrame to list of dictionaries
        employees = df.to_dict('records')
        
        # Save employee data
        with open(EMPLOYEE_DATA_FILE, 'w') as f:
            json.dump(employees, f)
        
        qr_codes = []
        # Generate QR codes for each employee
        for employee in employees:
            # Generate QR code
            qr_img = generate_qr_code(employee)
            
            # Save QR code
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            qr_filename = f"{employee['name']}_{timestamp}.png"
            qr_path = os.path.join(QR_CODE_DIR, qr_filename)
            qr_img.save(qr_path, 'PNG')
            
            # Add QR code path to employee data
            employee['qr_code_path'] = qr_path
            employee['qr_filename'] = qr_filename
            qr_codes.append({
                'name': employee['name'],
                'path': qr_path,
                'filename': qr_filename
            })
        
        return True, "QR codes generated successfully", qr_codes
    except Exception as e:
        return False, str(e), []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if not file.filename.endswith('.xlsx'):
        return jsonify({'success': False, 'message': 'Please upload an Excel file (.xlsx)'})
    
    # Save the uploaded file
    file_path = 'temp.xlsx'
    file.save(file_path)
    
    # Process the file
    success, message, qr_codes = process_excel_file(file_path)
    
    # Clean up
    os.remove(file_path)
    
    return jsonify({
        'success': success,
        'message': message,
        'qr_codes': qr_codes
    })

@app.route('/download/<filename>')
def download_qr(filename):
    try:
        return send_file(
            os.path.join(QR_CODE_DIR, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/employee/<name>')
def get_employee(name):
    try:
        with open(EMPLOYEE_DATA_FILE, 'r') as f:
            employees = json.load(f)
        
        employee = next((e for e in employees if e['name'] == name), None)
        if employee:
            return render_template('employee_details.html', employee=employee)
        return jsonify({'error': 'Employee not found'}), 404
    except:
        return jsonify({'error': 'Error reading employee data'}), 500

if __name__ == '__main__':
    app.run(debug=True) 