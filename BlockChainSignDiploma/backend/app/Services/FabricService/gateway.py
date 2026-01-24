"""
Fabric Gateway Service - Windows Docker Version
Sử dụng docker exec để chạy peer commands trong container fabric-tools
Không cần WSL, chạy hoàn toàn trên Windows
"""

import json
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.fabric_config import (
    FABRIC_CONFIG,
    get_cert_path,
    get_key_path,
    get_tls_cert_path,
    get_orderer_ca_path,
    validate_fabric_config
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class FabricGatewayService:
    """
    Service để kết nối và tương tác với Fabric Network
    Sử dụng Docker exec để chạy peer CLI trong container fabric-tools
    """
    
    def __init__(self):
        self.channel_name = FABRIC_CONFIG["channel_name"]
        self.chaincode_name = FABRIC_CONFIG["chaincode_name"]
        self.peer_endpoint = FABRIC_CONFIG["peer_endpoint"]
        self.msp_id = FABRIC_CONFIG["msp_id"]
        
        # Validate credentials exist
        validate_fabric_config()
        
        # Load credentials
        self.cert = self._read_file(get_cert_path())
        self.key = self._read_file(get_key_path())
        self.tls_cert = self._read_file(get_tls_cert_path())
        
        # Ensure crypto material exists in container
        cli_container = self._get_cli_container_name()
        self._ensure_crypto_in_container(cli_container)
        
        logger.info(f"✅ Fabric Gateway initialized for channel: {self.channel_name}")

    def _ensure_crypto_in_container(self, container_name: str):
        """
        Copy certificates from Host (Windows) to Container (/tmp)
        This ensures the backend works even if volumes are not mounted
        """
        try:
            logger.info(f"📦 Copying crypto material to container: {container_name}")
            
            # 1. Prepare Source Paths (Windows)
            # These paths rely on the user having run the 'cp' command from WSL earlier
            org_path = FABRIC_CONFIG["org_path"]
            
            # Admin MSP Dir
            admin_msp_src = org_path / "users" / "Admin@org1.example.com" / "msp"
            
            # Orderer TLS CA
            orderer_tls_src = get_orderer_ca_path()
            
            # Peer TLS CA
            peer_tls_src = get_tls_cert_path()
            
            # 2. Prepare Destination Paths (Container)
            # Must match what is used in _run_peer_command_in_docker
            
            # Create directories first
            subprocess.run(
                ["docker", "exec", container_name, "mkdir", "-p", "/tmp/crypto/admin_msp"],
                check=True
            )
            
            # 3. Execute Docker CP commands
            # Note: docker cp does not support renaming during copy, so we copy then rename or copy to dir
            
            # Copy Admin MSP
            # Destination: /tmp/crypto/admin_msp/msp
            subprocess.run(["docker", "cp", str(admin_msp_src), f"{container_name}:/tmp/crypto/admin_msp/"], check=True)
            
            # Copy Orderer TLS CA
            # Destination: /tmp/orderer.crt
            subprocess.run(["docker", "cp", str(orderer_tls_src), f"{container_name}:/tmp/orderer.crt"], check=True)
            
            # Copy Peer TLS CA (Org1)
            # Destination: /tmp/peer.crt
            subprocess.run(["docker", "cp", str(peer_tls_src), f"{container_name}:/tmp/peer.crt"], check=True)
            
            # Copy Peer TLS CA (Org2)
            # Destination: /tmp/peer_org2.crt
            # We construct the path relative to the FABRIC_NETWORK_PATH (parent of organizations)
            fabric_root = FABRIC_CONFIG["org_path"].parent.parent.parent # organizations/peerOrganizations/org1... -> NCKK Blockchain
            org2_tls_src = fabric_root / "organizations" / "peerOrganizations" / "org2.example.com" / "peers" / "peer0.org2.example.com" / "tls" / "ca.crt"
            subprocess.run(["docker", "cp", str(org2_tls_src), f"{container_name}:/tmp/peer_org2.crt"], check=True)
            
            logger.info("✅ Crypto material copied successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to copy crypto to container: {e}")
            # Don't raise here, let it fail at invocation if files are missing
            pass
    
    def _read_file(self, path: Path) -> bytes:
        """Read file content as bytes"""
        with open(path, 'rb') as f:
            return f.read()
    
    def _get_cli_container_name(self) -> str:
        """
        Tìm tên container peer hoặc cli đang chạy
        """
        try:
            # Get all running containers
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                containers = result.stdout.strip().split('\n')
                
                # Priority 1: cli or fabric-tools container
                for name in containers:
                    if 'cli' in name.lower() and 'dev-' not in name:
                        logger.info(f"Found CLI container: {name}")
                        return name
                
                # Priority 2: peer container (peer0.org1.example.com)
                for name in containers:
                    if 'peer0.org1.example.com' in name and 'dev-' not in name:
                        logger.info(f"Found peer container: {name}")
                        return name
                
                # Priority 3: any peer container
                for name in containers:
                    if 'peer' in name.lower() and 'dev-' not in name:
                        logger.info(f"Found peer container: {name}")
                        return name
            
            # Last fallback
            return "cli"
        except Exception as e:
            logger.warning(f"Could not find CLI container: {e}")
            return "cli"
    
    def _run_peer_command_in_docker(
        self,
        peer_args: list[str],
        is_query: bool = False
    ) -> subprocess.CompletedProcess:
        """
        Chạy peer command trong Docker container fabric-tools/cli
        
        Args:
            peer_args: Arguments cho peer command (không bao gồm 'peer')
            is_query: True nếu là query (read-only), False nếu là invoke (write)
        
        Returns:
            subprocess.CompletedProcess object
        """
        # Tìm container CLI
        cli_container = self._get_cli_container_name()
        
        # Build docker exec command
        # docker exec -e ... cli peer chaincode invoke/query ...
        # Build docker exec command
        # docker exec -e ... fabric-cli peer chaincode invoke/query ...
        
        # Use manually copied certificates for guaranteed match
        org1_tls_ca = "/tmp/peer.crt"
        orderer_ca = "/tmp/orderer.crt"
        
        # Admin MSP path (restored all keys)
        admin_msp = "/tmp/crypto/admin_msp/msp"
        
        docker_cmd = [
            "docker", "exec",
            "-e", "CORE_PEER_TLS_ENABLED=true",
            "-e", "CORE_PEER_LOCALMSPID=Org1MSP",
            "-e", f"CORE_PEER_TLS_ROOTCERT_FILE={org1_tls_ca}",
            "-e", f"CORE_PEER_MSPCONFIGPATH={admin_msp}",
            "-e", "CORE_PEER_ADDRESS=peer0.org1.example.com:7051",
            cli_container,
            "peer"
        ] + peer_args
        
        logger.info(f"🐳 Running in Docker: {' '.join(docker_cmd)}")
        
        # Execute
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8'
        )
        
        return result
    
    async def invoke_chaincode(
        self, 
        function: str, 
        args: list[str],
        transient_data: Optional[Dict[str, bytes]] = None
    ) -> Dict[str, Any]:
        """
        Invoke chaincode function (Write operation)
        
        Args:
            function: Tên function trong chaincode
            args: List arguments cho function
            transient_data: Dữ liệu tạm thời (không lưu lên ledger)
            
        Returns:
            Dict chứa kết quả transaction
        """
        try:
            logger.info(f"📤 Invoking chaincode: {function} with args: {args}")
            
            # Build fabric args
            fabric_args = json.dumps({"function": function, "Args": args})
            
            # Build fabric args
            fabric_args = json.dumps({"function": function, "Args": args})
            
            # Paths inside fabric-cli container (manually copied)
            orderer_ca = "/tmp/orderer.crt"
            org1_tls_ca = "/tmp/peer.crt"
            org2_tls_ca = "/tmp/peer_org2.crt"
            
            # Build peer command arguments
            orderer_address = "orderer.example.com:7050"
            
            peer_args = [
                "chaincode", "invoke",
                "-o", orderer_address,
                "--ordererTLSHostnameOverride", "orderer.example.com",
                "--tls",
                "--cafile", orderer_ca,
                "-C", self.channel_name,
                "-n", self.chaincode_name,
                "--peerAddresses", "peer0.org1.example.com:7051",
                "--tlsRootCertFiles", org1_tls_ca,
                "--peerAddresses", "peer0.org2.example.com:9051",
                "--tlsRootCertFiles", org2_tls_ca,
                "-c", fabric_args
            ]
            
            # Execute via Docker
            result = self._run_peer_command_in_docker(peer_args, is_query=False)
            
            if result.returncode == 0:
                logger.info(f"✅ Chaincode invoked successfully: {function}")
                return {
                    "success": True,
                    "function": function,
                    "message": "Transaction submitted successfully",
                    "output": result.stdout
                }
            else:
                logger.error(f"❌ Chaincode invoke failed: {result.stderr}")
                raise Exception(f"Chaincode invoke failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Error invoking chaincode: {str(e)}")
            raise
    
    async def query_chaincode(
        self, 
        function: str, 
        args: list[str]
    ) -> Any:
        """
        Query chaincode function (Read operation)
        
        Args:
            function: Tên function trong chaincode
            args: List arguments cho function
            
        Returns:
            Kết quả query (thường là dict hoặc list)
        """
        try:
            logger.info(f"🔍 Querying chaincode: {function} with args: {args}")
            
            # Build fabric args
            fabric_args = json.dumps({"function": function, "Args": args})
            
            # Build peer command arguments
            peer_args = [
                "chaincode", "query",
                "-C", self.channel_name,
                "-n", self.chaincode_name,
                "-c", fabric_args
            ]
            
            # Execute via Docker
            result = self._run_peer_command_in_docker(peer_args, is_query=True)
            
            if result.returncode == 0:
                # Parse JSON response
                stdout_str = result.stdout.strip()
                if not stdout_str:
                    logger.info(f"⚠️ Chaincode query returned empty response: {function}")
                    return None
                    
                response_data = json.loads(stdout_str)
                logger.info(f"✅ Chaincode query successful: {function}")
                return response_data
            else:
                logger.error(f"❌ Chaincode query failed: {result.stderr}")
                raise Exception(f"Chaincode query failed: {result.stderr}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse chaincode response: {str(e)}")
            logger.error(f"Raw output: {result.stdout}")
            raise
        except Exception as e:
            logger.error(f"❌ Error querying chaincode: {str(e)}")
            raise


# Singleton instance
_gateway_instance: Optional[FabricGatewayService] = None

def get_fabric_gateway() -> FabricGatewayService:
    """
    Get singleton instance of Fabric Gateway
    """
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = FabricGatewayService()
    return _gateway_instance
