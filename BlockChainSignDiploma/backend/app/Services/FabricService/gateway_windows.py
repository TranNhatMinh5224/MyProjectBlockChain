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
        
        logger.info(f"✅ Fabric Gateway initialized for channel: {self.channel_name}")
    
    def _read_file(self, path: Path) -> bytes:
        """Read file content as bytes"""
        with open(path, 'rb') as f:
            return f.read()
    
    def _get_cli_container_name(self) -> str:
        """
        Tìm tên container fabric-tools đang chạy
        Hoặc trả về tên mặc định nếu chưa có
        """
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=cli", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
            
            # Fallback: tên container mặc định trong test-network
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
        # docker exec cli peer chaincode invoke/query ...
        docker_cmd = [
            "docker", "exec",
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
            
            # Build peer command arguments
            peer_args = [
                "chaincode", "invoke",
                "-o", FABRIC_CONFIG["orderer_endpoint"],
                "--tls",
                "--cafile", "/opt/gopath/src/github.com/hyperledger/fabric/peer/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem",
                "-C", self.channel_name,
                "-n", self.chaincode_name,
                "--peerAddresses", self.peer_endpoint,
                "--tlsRootCertFiles", "/opt/gopath/src/github.com/hyperledger/fabric/peer/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt",
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
                response_data = json.loads(result.stdout.strip())
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
