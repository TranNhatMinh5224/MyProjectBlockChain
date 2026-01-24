package main

import (
	"crypto/sha256"
	"fmt"
	"math/big"

	"go-custom-curve/crypto"
	"go-custom-curve/curve"
)

func main() {
	fmt.Println("=== DEMO: Go Custom Curve Sign/Verify ===")

	// 1. Generate Key
	privateKey, _ := curve.GenerateRandomKey()
	fmt.Printf("Private Key: 0x%x\n", privateKey)

	publicKey := curve.GenerateBasePoint().ScalarMult(privateKey)
	fmt.Printf("Public Key: (0x%x, 0x%x)\n", publicKey.X, publicKey.Y)

	// 2. Hash Message
	msg := "Hello Blockchain Diploma"
	hash := sha256.Sum256([]byte(msg))
	hashInt := new(big.Int).SetBytes(hash[:])
	fmt.Printf("Message Hash: 0x%x\n", hash)

	// 3. Sign
	r, s, err := crypto.Sign(hashInt, privateKey)
	if err != nil {
		fmt.Printf("Sign error: %v\n", err)
		return
	}
	fmt.Printf("Signature: (r=0x%x, s=0x%x)\n", r, s)

	// 4. Verify
	valid := crypto.Verify(hashInt, r, s, publicKey)
	if valid {
		fmt.Println("✅ Verify SUCCESS!")
	} else {
		fmt.Println("❌ Verify FAILED!")
	}

	// Test fail
	// hashInt.Add(hashInt, big.NewInt(1))
	// valid = crypto.Verify(hashInt, r, s, publicKey)
	// fmt.Println("Tampered message verify:", valid)
}
