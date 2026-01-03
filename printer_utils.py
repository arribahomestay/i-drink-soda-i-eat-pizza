"""
Printer utility for POS System
Handles printing receipts to default printer on Windows
"""
import os
import sys
import subprocess
from pathlib import Path


def print_image_to_default_printer(image_path):
    """
    Print an image file to the default printer (optimized for 80mm thermal printers)
    
    Args:
        image_path: Path to the image file (PNG, BMP, JPG)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return False, f"File not found: {image_path}"
        
        # Convert to absolute path
        abs_path = os.path.abspath(image_path)
        
        # Windows printing - optimized for thermal printers
        if sys.platform == 'win32':
            try:
                # Method 1: Direct PowerShell printing (best for thermal printers)
                # This method sends the image directly to the printer without dialogs
                ps_script = f'''
                Add-Type -AssemblyName System.Drawing
                Add-Type -AssemblyName System.Drawing.Printing
                
                # Get default printer
                $printerSettings = New-Object System.Drawing.Printing.PrinterSettings
                $printerName = $printerSettings.PrinterName
                
                # Load image
                $image = [System.Drawing.Image]::FromFile("{abs_path}")
                
                # Create print document
                $printDoc = New-Object System.Drawing.Printing.PrintDocument
                $printDoc.PrinterSettings.PrinterName = $printerName
                
                # Set to not use default margins (important for thermal printers)
                $printDoc.DefaultPageSettings.Margins = New-Object System.Drawing.Printing.Margins(0, 0, 0, 0)
                
                # Print event handler
                $printPage = {{
                    param($sender, $ev)
                    
                    # Get page bounds
                    $bounds = $ev.PageBounds
                    
                    # For thermal printers, print at actual size without scaling
                    # This prevents endless paper feed
                    $destRect = New-Object System.Drawing.Rectangle(0, 0, $image.Width, $image.Height)
                    
                    # Draw image
                    $ev.Graphics.DrawImage($image, $destRect)
                    
                    # No more pages
                    $ev.HasMorePages = $false
                }}
                
                # Register event
                $printDoc.add_PrintPage($printPage)
                
                # Print
                $printDoc.Print()
                
                # Cleanup
                $image.Dispose()
                $printDoc.Dispose()
                
                Write-Output "Success"
                '''
                
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                
                if result.returncode == 0 and "Success" in result.stdout:
                    return True, "Printed successfully"
                else:
                    # Fallback method: Use win32print if available
                    try:
                        import win32print
                        import win32ui
                        from PIL import Image, ImageWin
                        import win32con
                        
                        # Get default printer
                        printer_name = win32print.GetDefaultPrinter()
                        
                        # Open the image
                        img = Image.open(abs_path)
                        
                        # Create a device context
                        hDC = win32ui.CreateDC()
                        hDC.CreatePrinterDC(printer_name)
                        
                        # Start the print job
                        hDC.StartDoc(abs_path)
                        hDC.StartPage()
                        
                        # For thermal printers: print at actual pixel size
                        # This prevents scaling issues that cause endless paper feed
                        img_width, img_height = img.size
                        
                        # Convert image to bitmap and print at actual size
                        dib = ImageWin.Dib(img)
                        dib.draw(hDC.GetHandleOutput(), (0, 0, img_width, img_height))
                        
                        # End the print job
                        hDC.EndPage()
                        hDC.EndDoc()
                        hDC.DeleteDC()
                        
                        return True, f"Printed to {printer_name}"
                        
                    except ImportError:
                        # Final fallback: Simple Windows print
                        os.startfile(abs_path, "print")
                        return True, "Print job sent (may require confirmation)"
                        
            except Exception as e:
                return False, f"Printing failed: {str(e)}"
        else:
            # For non-Windows systems (Linux/Mac)
            try:
                # Linux: Use lp command
                subprocess.run(["lp", abs_path], check=True, timeout=10)
                return True, "Print job sent to default printer (Linux)"
            except:
                try:
                    # Mac: Use lpr command
                    subprocess.run(["lpr", abs_path], check=True, timeout=10)
                    return True, "Print job sent to default printer (Mac)"
                except Exception as e:
                    return False, f"Printing not supported on this platform: {str(e)}"
    
    except Exception as e:
        return False, f"Printing error: {str(e)}"


def print_receipt_silent(image_path):
    """
    Silently print receipt without showing dialogs
    
    Args:
        image_path: Path to the receipt image
    
    Returns:
        bool: True if successful, False otherwise
    """
    success, message = print_image_to_default_printer(image_path)
    return success


def get_default_printer():
    """
    Get the name of the default printer
    
    Returns:
        str: Name of default printer or None
    """
    try:
        if sys.platform == 'win32':
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                "Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows")
            printer_name = winreg.QueryValueEx(key, "Device")[0]
            winreg.CloseKey(key)
            # Format: "PrinterName,winspool,Port"
            return printer_name.split(',')[0] if printer_name else None
        else:
            # Linux/Mac
            result = subprocess.run(
                ["lpstat", "-d"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Output format: "system default destination: PrinterName"
                output = result.stdout.strip()
                if ":" in output:
                    return output.split(":")[-1].strip()
            return None
    except:
        return None


def check_printer_available():
    """
    Check if a default printer is available
    
    Returns:
        tuple: (available: bool, printer_name: str or None)
    """
    printer = get_default_printer()
    return (printer is not None, printer)
