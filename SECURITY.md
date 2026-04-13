# Security Policy

## Supported Firmware

This project supports CPFlight firmware versions configured in the `config/cpflight.json` file.

Supported configurations:

- LAN firmware: PRO611  
- USB firmware compatibility: 127  

These values are defined inside:

config/cpflight.json

Example:
{
  "FW_COMPATIBLE": "PRO611",
  "USB_FW_COMPATIBLE": "127"
}

Only these firmware configurations are officially tested and supported.

---

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

Do NOT open a public issue.

Instead, use:
- GitHub Security Advisories (preferred)
- Or contact the maintainer via GitHub profile

---

## Response Policy

- Acknowledgment within a few days  
- Valid issues will be investigated and fixed  
- Invalid reports may be closed with explanation  

---

## Security Scope

This project includes:
- Network communication between CPFlight and MSFS 2020/2024
- Serial hardware communication
- Data exchange with Fenix A32x integration

---

## Notes

Firmware compatibility is defined by the developer and shipped with each official release in `config/cpflight.json`.

> These values MUST NOT be modified by users.

Only official releases from the maintainer may change firmware compatibility settings.

Changing these values manually is not supported and may cause unexpected behavior or loss of functionality.
