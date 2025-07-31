# CPFLIGHT FCU/EFIS Compatibility with Fenix A320 in FS2020/FS2024

## Description

This is a Python project designed to enable compatibility between CPFLIGHT's FCU and EFIS modules and the Fenix A320 aircraft in Microsoft Flight Simulator 2020 (FS2020) and Microsoft Flight Simulator 2024 (FS2024).

The goal is to allow smooth and realistic integration between CPFLIGHT hardware and the Fenix A320 virtual cockpit, ensuring accurate and responsive synchronization of controls.

## Requirements

- Python 3.8 or higher  
- Local network connection to the PC running MSFS  
- CPFLIGHT modules connected via USB or serial  
- Fenix A320 installed  
- FS2020 or FS2024 properly configured  

## Main Features

- Bi-directional communication between CPFLIGHT FCU/EFIS and the Fenix A320  
- Real-time data read/write and synchronization  
- Modular architecture ready for future expansion and other hardware  

## Project Status

Actively under development.  
Contributions, testing, and bug reports are welcome.

## Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/Butzy79/CpFlightFcu.git
    ```
2. Install dependencies:
   ```bash
    pip install -r requirements.txt
   ```
   
3. Run the main script:
   ```bash
   python main.py
   ```
## Project Structure
- main.py — Main execution script
- modules/ — Hardware and simulator interface logic
- config/ — Configuration files
- docs/ — Additional documentation

## License
This project is licensed under the MIT License.
See the LICENSE file for details.

## Contact
For issues, suggestions, or collaboration, please open an issue on GitHub or contact the developer.
