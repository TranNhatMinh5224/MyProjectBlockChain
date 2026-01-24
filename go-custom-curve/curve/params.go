package curve

import (
	"fmt"
	"math/big"
)

// Curve represents the TNM5224 Elliptic Curve parameters
type Curve struct {
	Name string
	P    *big.Int // Prime modulus
	A    *big.Int // Coefficient A
	B    *big.Int // Coefficient B
	Gx   *big.Int // Generator X
	Gy   *big.Int // Generator Y
	N    *big.Int // Order of G
	H    *big.Int // Cofactor
}

var TNM5224 *Curve

func init() {
	// Initialize Curve Parameters from Python definition
	TNM5224 = &Curve{
		Name: "TNM5224",
		P:    fromHex("b63c11d43e09b729962d47edb6ddab7a929ed7aa6e7f01da8ca3f72022037373"),
		A:    fromHex("b63c11d43e09b729962d47edb6ddab7a929ed7aa6e7f01da8ca3f72022037370"),
		B:    fromHex("9ced8b5e0375c92d55fff25924233e0ca2338392d8c8bcc2d8b42b0fe1418a95"),
		Gx:   fromHex("61fec3112fa5e7aa1779cc56bcf2bdd7326982cc69693bc92908fedf007dffd9"),
		Gy:   fromHex("0890dd8c564d7601b0a8e4ce5aba2ad6a3bad24deb8d1e1b6f18d0beb70e1c1d"),
		N:    fromHex("b63c11d43e09b729962d47edb6ddab7ba1a80e44874c71dfbf9419280fa3d971"),
		H:    big.NewInt(1),
	}
}

// fromHex helper
func fromHex(s string) *big.Int {
	i, ok := new(big.Int).SetString(s, 16)
	if !ok {
		fmt.Printf("Error parsing hex: %s\n", s)
		return nil
	}
	return i
}
