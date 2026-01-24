"""
Fabric Network Configuration
Cấu hình kết nối đến Hyperledger Fabric Network
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent

# UPDATE: Using Local Copy on Windows (Stable Access)
# User copied 'organizations' folder to Desktop project root
FABRIC_NETWORK_PATH = Path(r"C:\Users\Admin\Desktop\NCKK Blockchain")

# Fabric Network Configuration
FABRIC_CONFIG = {
    # Channel and Chaincode
    "channel_name": "mychannel",
    "chaincode_name": "diploma", 
    
    # Organization
    "msp_id": "Org1MSP",
    
    # Endpoints
    "peer_endpoint": "localhost:7051",
    "orderer_endpoint": "localhost:7050",
    
    # Credentials paths (relative to fabric-samples/test-network)
    "org_path": FABRIC_NETWORK_PATH / "organizations" / "peerOrganizations" / "org1.example.com",
}

# Certificate paths
def get_cert_path():
    """Get path to user certificate"""
    org_path = FABRIC_CONFIG["org_path"]
    return org_path / "users" / "Admin@org1.example.com" / "msp" / "signcerts" / "cert.pem"

def get_key_path():
    """Get path to user private key"""
    org_path = FABRIC_CONFIG["org_path"]
    key_dir = org_path / "users" / "Admin@org1.example.com" / "msp" / "keystore"
    # Get first key file in keystore directory
    key_files = list(key_dir.glob("*_sk"))
    if key_files:
        return key_files[0]
    raise FileNotFoundError(f"No private key found in {key_dir}")

def get_tls_cert_path():
    """Get path to peer TLS certificate"""
    org_path = FABRIC_CONFIG["org_path"]
    return org_path / "peers" / "peer0.org1.example.com" / "tls" / "ca.crt"

def get_orderer_ca_path():
    """Get path to orderer TLS CA certificate"""
    return FABRIC_NETWORK_PATH / "organizations" / "ordererOrganizations" / "example.com" / "orderers" / "orderer.example.com" / "tls" / "ca.crt"

# Validate configuration
def validate_fabric_config():
    """
    Validate that all required Fabric credentials exist
    Raises FileNotFoundError if any required file is missing
    """
    try:
        cert_path = get_cert_path()
        key_path = get_key_path()
        tls_cert_path = get_tls_cert_path()
        
        if not cert_path.exists():
            raise FileNotFoundError(f"Certificate not found: {cert_path}")
        if not key_path.exists():
            raise FileNotFoundError(f"Private key not found: {key_path}")
        if not tls_cert_path.exists():
            raise FileNotFoundError(f"TLS certificate not found: {tls_cert_path}")
            
        return True
    except Exception as e:
        raise FileNotFoundError(
            f"Fabric credentials not found. "
            f"Please ensure Fabric network is running and credentials exist in: "
            f"{FABRIC_CONFIG['org_path']}\n"
            f"Error: {str(e)}"
        )
