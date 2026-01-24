"""
CRYPTO HELPER FUNCTIONS
========================
Helper functions để tích hợp thư viện ký số custom vào backend
"""

from custom_curve_signature.keygen import generate_keypair
from custom_curve_signature.hash import hash_msg
from custom_curve_signature.sign import sign
from custom_curve_signature.verify import verify
from custom_curve_signature.point import Point
import json
from typing import Tuple, Dict, Any


def generate_university_keypair() -> Tuple[str, str]:
    """
    Generate cặp khóa cho trường đại học
    
    Returns:
        Tuple[str, str]: (private_key_hex, public_key_hex)
        - private_key_hex: hex string của private key
        - public_key_hex: "hex_x,hex_y" format
    """
    private_key, public_key = generate_keypair()
    
    # Convert to hex strings
    private_key_hex = hex(private_key)
    public_key_hex = f"{hex(public_key.x)},{hex(public_key.y)}"
    
    return private_key_hex, public_key_hex


def derive_public_key(private_key_hex: str) -> str:
    """
    Derive public key từ private key
    
    Args:
        private_key_hex: Private key hex string
        
    Returns:
        str: Public key "hex_x,hex_y" format
    """
    # Parse private key
    private_key_int = int(private_key_hex, 16)
    
    # Generate temporary keypair to get curve
    _, temp_pub = generate_keypair()
    
    # Create generator point G from curve parameters
    G = Point(temp_pub.curve.Gx, temp_pub.curve.Gy, curve=temp_pub.curve)
    
    # Compute public key: Q = private_key * G
    public_key = G.multiply(private_key_int)
    
    # Format as hex string
    public_key_hex = f"{hex(public_key.x)},{hex(public_key.y)}"
    
    return public_key_hex


def hash_diploma_data(diploma_data: Dict[str, Any]) -> str:
    """
    Hash dữ liệu bằng cấp để ký
    
    Args:
        diploma_data: Dictionary chứa thông tin bằng
        
    Returns:
        str: Hash hex string
    """
    # Convert dict to JSON string (sorted keys for consistency)
    json_str = json.dumps(diploma_data, sort_keys=True, ensure_ascii=False)
    
    # Hash the JSON bytes
    hash_int = hash_msg(json_str.encode('utf-8'))
    
    return hex(hash_int)


def sign_diploma(diploma_data: Dict[str, Any], private_key_hex: str) -> Tuple[str, str]:
    """
    Ký bằng cấp với private key của trường
    
    Args:
        diploma_data: Dictionary chứa thông tin bằng
        private_key_hex: Private key hex string
        
    Returns:
        Tuple[str, str]: (hash_hex, signature_hex)
        - hash_hex: Hash của data
        - signature_hex: "hex_r,hex_s" format
    """
    # Hash data
    hash_hex = hash_diploma_data(diploma_data)
    hash_int = int(hash_hex, 16)
    
    # Parse private key
    private_key_int = int(private_key_hex, 16)
    
    # Sign
    signature = sign(hash_int, private_key_int)
    
    # Format signature
    if isinstance(signature, tuple):
        sig_r, sig_s = signature[0], signature[1]
    else:
        sig_r, sig_s = signature.r, signature.s
    
    signature_hex = f"{hex(sig_r)},{hex(sig_s)}"
    
    return hash_hex, signature_hex


def verify_diploma_signature(
    diploma_data: Dict[str, Any],
    signature_hex: str,
    public_key_hex: str,
    stored_hash_hex: str = None
) -> Tuple[bool, str]:
    """
    Verify chữ ký bằng cấp
    
    Args:
        diploma_data: Dictionary chứa thông tin bằng
        signature_hex: Signature "hex_r,hex_s" format
        public_key_hex: Public key "hex_x,hex_y" format
        stored_hash_hex: Hash đã lưu (optional, để check consistency)
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    try:
        # Hash data
        computed_hash_hex = hash_diploma_data(diploma_data)
        
        # Check hash consistency nếu có stored hash
        if stored_hash_hex and computed_hash_hex != stored_hash_hex:
            return False, "Hash mismatch: diploma data has been modified"
        
        # Parse hash
        hash_int = int(computed_hash_hex, 16)
        
        # Parse signature
        sig_parts = signature_hex.split(',')
        if len(sig_parts) != 2:
            return False, "Invalid signature format"
        sig_r = int(sig_parts[0], 16)
        sig_s = int(sig_parts[1], 16)
        signature_tuple = (sig_r, sig_s)
        
        # Parse public key and recreate Point
        pub_parts = public_key_hex.split(',')
        if len(pub_parts) != 2:
            return False, "Invalid public key format"
        pub_x = int(pub_parts[0], 16)
        pub_y = int(pub_parts[1], 16)
        
        # Get curve from a temporary keypair (to get curve object)
        _, temp_pub = generate_keypair()
        public_key = Point(pub_x, pub_y, curve=temp_pub.curve)
        
        # Verify signature
        is_valid = verify(hash_int, signature_tuple, public_key)
        
        if is_valid:
            return True, "Signature is valid"
        else:
            return False, "Invalid signature"
            
    except Exception as e:
        return False, f"Verification error: {str(e)}"


def verify_file_signature(
    file_hash_hex: str,
    signature_hex: str,
    public_key_hex: str
) -> Tuple[bool, str]:
    """
    Verify chữ ký của một file dựa trên hash của nó
    
    Args:
        file_hash_hex: Hash SHA256 của file (hex string)
        signature_hex: Signature "hex_r,hex_s" format
        public_key_hex: Public key "hex_x,hex_y" format
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    try:
        # Parse hash (Dữ liệu đầu vào của hàm verify của signature lib là 1 số nguyên lớn)
        # Tuy nhiên hash_msg trong lib thường hash lại. 
        # Cần check xem hash_msg trong lib có hash lần nữa không.
        # Ở sign_diploma: hash_int = hash_msg(json_str.encode)
        # Nếu đã có file hash sẵn, ta cần convert hex -> int
        
        # NOTE: logic verify của lib verify(hash_int, ...)
        # Ta giả sử file_hash_hex là kết quả của SHA256 rồi.
        hash_int = int(file_hash_hex, 16)
        
        # Parse signature
        sig_parts = signature_hex.split(',')
        if len(sig_parts) != 2:
            return False, "Invalid signature format"
        sig_r = int(sig_parts[0], 16)
        sig_s = int(sig_parts[1], 16)
        signature_tuple = (sig_r, sig_s)
        
        # Parse public key
        pub_parts = public_key_hex.split(',')
        if len(pub_parts) != 2:
            return False, "Invalid public key format"
        pub_x = int(pub_parts[0], 16)
        pub_y = int(pub_parts[1], 16)
        
        # Get curve
        _, temp_pub = generate_keypair()
        public_key = Point(pub_x, pub_y, curve=temp_pub.curve)
        
        # Verify
        is_valid = verify(hash_int, signature_tuple, public_key)
        
        if is_valid:
            return True, "Signature is valid"
        else:
            return False, "Invalid signature"
            
    except Exception as e:
        return False, f"Verification error: {str(e)}"
