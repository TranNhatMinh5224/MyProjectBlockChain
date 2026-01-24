"""
Fabric Gateway Service
Quản lý kết nối và giao tiếp với Hyperledger Fabric Network
"""

import grpc
import json
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
    Sử dụng gRPC để gọi chaincode
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
            
        Example:
            result = await gateway.invoke_chaincode(
                "RegisterSchool",
                ["HUST", "Hanoi University...", "0xPUBKEY", "0xCERT", "2024-01-01"]
            )
        """
        try:
            logger.info(f"📤 Invoking chaincode: {function} with args: {args}")
            
            # TODO: Implement actual gRPC call to Fabric Gateway
            # For now, we'll use peer CLI as a workaround
            # In production, use fabric-gateway library
            
            import subprocess
            import os
            
            # Set environment variables
            env = os.environ.copy()
            env.update({
                "CORE_PEER_TLS_ENABLED": "true",
                "CORE_PEER_LOCALMSPID": self.msp_id,
                "CORE_PEER_ADDRESS": self.peer_endpoint,
                "CORE_PEER_TLS_ROOTCERT_FILE": str(get_tls_cert_path()),
                "CORE_PEER_MSPCONFIGPATH": str(get_cert_path().parent.parent),
            })
            
            # Build peer command
            fabric_args = json.dumps({"function": function, "Args": args})
            
            # --- WINDOWS SUPPORT: Run via WSL ---
            if os.name == 'nt': # Windows
                # Convert Windows paths to WSL paths
                def to_wsl_path(win_path):
                    if not win_path: return ""
                    # Convert drive letter (e.g., C:\ -> /mnt/c/)
                    path_str = str(win_path).replace('\\', '/')
                    if ':' in path_str:
                        drive, rest = path_str.split(':', 1)
                        return f"/mnt/{drive.lower()}{rest}"
                    # HandleUNC path (\\wsl.localhost\Ubuntu\...) -> /...
                    if path_str.startswith('//wsl.localhost/Ubuntu'):
                        return path_str.replace('//wsl.localhost/Ubuntu', '')
                    return path_str

                # Update ENV paths for WSL context
                # Note: On Windows via WSL, we pass ENV vars via the command line or assume WSL env
                # But subprocess.run with 'wsl' inherits the WSL var if we set it? 
                # Better approach: export vars in the command string or use -e flag (if wsl supports it easily)
                # Simple approach: Construct the full bash command string
                
                wsl_tls_cert = to_wsl_path(str(get_tls_cert_path()))
                wsl_orderer_ca = to_wsl_path(str(get_orderer_ca_path()))
                wsl_msp_config = to_wsl_path(str(get_cert_path().parent.parent))
                
                # Construct command to run inside WSL
                # We need to set env vars INSIDE wsl
                # AND ensure 'peer' binary is in PATH
                # FIX: Use clean PATH to avoid Windows path issues (spaces, parens)
                # AND set FABRIC_CFG_PATH for peer CLI
                bash_cmd = (
                    f"export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/namnguyen/fabric-samples/bin && "
                    f"export FABRIC_CFG_PATH=/home/namnguyen/fabric-samples/config && "
                    f"export CORE_PEER_TLS_ENABLED=true && "
                    f"export CORE_PEER_LOCALMSPID={self.msp_id} && "
                    f"export CORE_PEER_ADDRESS={self.peer_endpoint} && "
                    f"export CORE_PEER_TLS_ROOTCERT_FILE='{wsl_tls_cert}' && "
                    f"export CORE_PEER_MSPCONFIGPATH='{wsl_msp_config}' && "
                    f"peer chaincode invoke "
                    f"-o {FABRIC_CONFIG['orderer_endpoint']} "
                    f"--tls --cafile '{wsl_orderer_ca}' "
                    f"-C {self.channel_name} "
                    f"-n {self.chaincode_name} "
                    f"-c '{fabric_args}'"
                )
                
                logger.info(f"Running in WSL: {bash_cmd}")
                cmd = ["wsl", "bash", "-c", bash_cmd]
                
            else:
                # Linux/Native Logic
                cmd = [
                    "peer", "chaincode", "invoke",
                    "-o", FABRIC_CONFIG["orderer_endpoint"],
                    "--tls", "--cafile", str(get_tls_cert_path()),
                    "-C", self.channel_name,
                    "-n", self.chaincode_name,
                    "-c", fabric_args
                ]

            # Execute command
            result = subprocess.run(
                cmd,
                env=env if os.name != 'nt' else None, # Windows WSL doesn't need Python process env
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8' # Force utf-8
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Chaincode invoked successfully: {function}")
                return {
                    "success": True,
                    "function": function,
                    "message": "Transaction submitted successfully"
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
            
        Example:
            school = await gateway.query_chaincode("GetSchool", ["HUST"])
        """
        try:
            logger.info(f"🔍 Querying chaincode: {function} with args: {args}")
            
            import subprocess
            import os
            
            # Set environment variables
            env = os.environ.copy()
            env.update({
                "CORE_PEER_TLS_ENABLED": "true",
                "CORE_PEER_LOCALMSPID": self.msp_id,
                "CORE_PEER_ADDRESS": self.peer_endpoint,
                "CORE_PEER_TLS_ROOTCERT_FILE": str(get_tls_cert_path()),
                "CORE_PEER_MSPCONFIGPATH": str(get_cert_path().parent.parent),
            })
            
            # Build peer command
            fabric_args = json.dumps({"function": function, "Args": args})
            
            # --- WINDOWS SUPPORT: Run via WSL ---
            if os.name == 'nt': # Windows
                # Convert Windows paths to WSL paths
                def to_wsl_path(win_path):
                    if not win_path: return ""
                    path_str = str(win_path).replace('\\', '/')
                    if ':' in path_str:
                        drive, rest = path_str.split(':', 1)
                        return f"/mnt/{drive.lower()}{rest}"
                    if path_str.startswith('//wsl.localhost/Ubuntu'):
                        return path_str.replace('//wsl.localhost/Ubuntu', '')
                    return path_str

                wsl_tls_cert = to_wsl_path(str(get_tls_cert_path()))
                wsl_msp_config = to_wsl_path(str(get_cert_path().parent.parent))
                
                # Construct command to run inside WSL
                bash_cmd = (
                    f"export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/namnguyen/fabric-samples/bin && "
                    f"export FABRIC_CFG_PATH=/home/namnguyen/fabric-samples/config && "
                    f"export CORE_PEER_TLS_ENABLED=true && "
                    f"export CORE_PEER_LOCALMSPID={self.msp_id} && "
                    f"export CORE_PEER_ADDRESS={self.peer_endpoint} && "
                    f"export CORE_PEER_TLS_ROOTCERT_FILE='{wsl_tls_cert}' && "
                    f"export CORE_PEER_MSPCONFIGPATH='{wsl_msp_config}' && "
                    f"peer chaincode query "
                    f"-C {self.channel_name} "
                    f"-n {self.chaincode_name} "
                    f"-c '{fabric_args}'"
                )
                
                logger.info(f"Running in WSL: {bash_cmd}")
                cmd = ["wsl", "bash", "-c", bash_cmd]
                
            else:
                # Linux/Native Logic
                cmd = [
                    "peer", "chaincode", "query",
                    "-C", self.channel_name,
                    "-n", self.chaincode_name,
                    "-c", fabric_args
                ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                env=env if os.name != 'nt' else None,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8' # Force utf-8
            )
            
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
