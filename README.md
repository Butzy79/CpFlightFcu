# CPFLIGHT FCU/EFIS Compatibility with Fenix A320 in FS2020/FS2024

## Description
This is a Python project designed to enable compatibility between CPFLIGHT's FCU and EFIS modules and the Fenix A320 aircraft in Microsoft Flight Simulator 2020 (FS2020) and Microsoft Flight Simulator 2024 (FS2024).

It provides realistic, real-time synchronization between CPFLIGHT hardware and the virtual cockpit.

## Requirements

- Python 3.8 or higher  
- Local network connection to the PC running MSFS 
- CPFLIGHT modules connected via USB or serial  
- Fenix A320 installed  
- FS2020 or FS2024 properly configured  
- MobiFlight installed along with its WASM module
- ***CpFlight Firmware FCU VERSION 611***

## Main Features

- Bi-directional communication between CPFLIGHT FCU/EFIS and the Fenix A320  
- Real-time data read/write and synchronization  
- Modular architecture ready for future expansion and other hardware  

# Usage

1. For Users Who Just Want to **Use the Software**
---------------------------------------------------
1. Download the latest release from GitHub:
   https://github.com/Butzy79/CpFlightFcu/releases
2. Download `CpFlight_Control_CFC_xxx.zip` (xxx = version) and **extract it** to a folder.
3. Edit the file `config/cpflight.json` with your IP address and port. Default port is 4500.
   
Example:
```json
   {
       ...
       "IP": "10.2.0.2",
       "PORT": 4500,
       ...
   }
```
4. Run the executable `CpFlight_Controller.exe`.

***No need to install Python or compile anything.***

# For Users Who Want to **Contribute or Use the Source Code**

## Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/Butzy79/CpFlightFcu.git
    ```
   
2. Install dependencies:
   ```bash
    pip install -r requirements.txt
   ```

3. Edit the file `config/cpflight.json` with your IP address and communication port
By default, the port is set to `4500`.
```json
{
    ...
    "IP": "10.2.0.2",
    "PORT": 4500,
    ...
}
```

4. Run the main script:
   ```bash
   python main.py
   ```

## Test commands and listener:
1. Send commands to unit:
   ```bash
   python ./tests/send_commands.py
   ```
2. Sniffing commands sent to unit:
   ```bash
   python ./tests/sniff_commands.py
   ```
   
## Project Structure
- main.py — Main execution script
- modules/ — Hardware and simulator interface logic
- config/ — Configuration files
- docs/ — Additional documentation

## Create EXE file
Build environment:
```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
```
Create Version
```
py gen_version.py
pyinstaller --onefile --noconsole --name CpFlight_Controller main.py --hidden-import SimConnect --hidden-import scapi --hidden-import requests --hidden-import packaging --add-binary ".venv\Lib\site-packages\SimConnect\SimConnect.dll;SimConnect" --icon=resources/butzy.ico --add-data "resources/butzy.ico;resources"
```

## License
This project is licensed under the MIT License.
See the LICENSE file for details.

## Contact
For issues, suggestions, or collaboration, please open an issue on GitHub or contact the developer.
