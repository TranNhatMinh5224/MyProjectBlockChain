package main

import (
	"crypto/elliptic"
	"math/big"
)

// TNM5224 returns the CurveParams for the custom TNM5224 curve
// y^2 = x^3 + ax + b  (with a = -3)
func TNM5224() elliptic.Curve {
	p, _ := new(big.Int).SetString("b63c11d43e09b729962d47edb6ddab7a929ed7aa6e7f01da8ca3f72022037373", 16)
	n, _ := new(big.Int).SetString("b63c11d43e09b729962d47edb6ddab7ba1a80e44874c71dfbf9419280fa3d971", 16)
	b, _ := new(big.Int).SetString("9ced8b5e0375c92d55fff25924233e0ca2338392d8c8bcc2d8b42b0fe1418a95", 16)
	gx, _ := new(big.Int).SetString("61fec3112fa5e7aa1779cc56bcf2bdd7326982cc69693bc92908fedf007dffd9", 16)
	gy, _ := new(big.Int).SetString("0890dd8c564d7601b0a8e4ce5aba2ad6a3bad24deb8d1e1b6f18d0beb70e1c1d", 16)

	curve := &elliptic.CurveParams{
		P:       p,
		N:       n,
		B:       b,
		Gx:      gx,
		Gy:      gy,
		BitSize: 256,
		Name:    "TNM5224",
	}
	return curve
}
