package crypto

import (
	"fmt"
	"go-custom-curve/curve"
	"math/big"
)

// Sign signs a message hash
func Sign(messageHash *big.Int, privateKey *big.Int) (*big.Int, *big.Int, error) {
	n := curve.TNM5224.N
	G := curve.GenerateBasePoint()

	if privateKey.Cmp(big.NewInt(1)) < 0 || privateKey.Cmp(n) >= 0 {
		return nil, nil, fmt.Errorf("invalid private key")
	}

	// 1. Generate k (RFC 6979)
	k := GenerateK_RFC6979(n, privateKey, messageHash)

	// 2. R = k * G
	R := G.ScalarMult(k)
	r := new(big.Int).Mod(R.X, n)

	if r.Sign() == 0 {
		// Extremely rare
		return nil, nil, fmt.Errorf("invalid r (zero)")
	}

	// 3. s = k^-1 * (m + r*d) mod n
	kInv := new(big.Int).ModInverse(k, n)

	sTop := new(big.Int).Mul(r, privateKey)
	sTop.Add(sTop, messageHash)

	s := new(big.Int).Mul(kInv, sTop)
	s.Mod(s, n)

	if s.Sign() == 0 {
		return nil, nil, fmt.Errorf("invalid s (zero)")
	}

	// 4. Low-S Normalization
	// if s > n/2 then s = n - s
	halfN := new(big.Int).Div(n, big.NewInt(2))
	if s.Cmp(halfN) > 0 {
		s.Sub(n, s)
	}

	return r, s, nil
}

// Verify verifies a signature
func Verify(messageHash *big.Int, r, s *big.Int, publicKey *curve.Point) bool {
	n := curve.TNM5224.N

	// Check r, s range
	if r.Cmp(big.NewInt(1)) < 0 || r.Cmp(n) >= 0 {
		return false
	}
	if s.Cmp(big.NewInt(1)) < 0 || s.Cmp(n) >= 0 {
		return false
	}

	// Check Public Key
	if publicKey.IsInfinity() {
		return false
	}
	// TODO: Add IsOnCurve check (already implicit in construction usually but good to check)
	// We missed strict IsOnCurve in point.go, but for now we trust inputs or add later.

	// w = s^-1
	w := new(big.Int).ModInverse(s, n)

	// u1 = m * w
	u1 := new(big.Int).Mul(messageHash, w)
	u1.Mod(u1, n)

	// u2 = r * w
	u2 := new(big.Int).Mul(r, w)
	u2.Mod(u2, n)

	// X = u1*G + u2*P
	G := curve.GenerateBasePoint()

	// X = u1*G
	Term1 := G.ScalarMult(u1)
	// Y = u2*P
	Term2 := publicKey.ScalarMult(u2)

	X := Term1.Add(Term2)
	X = X.ToAffine()

	if X.IsInfinity() {
		return false
	}

	// v = X.x mod n
	v := new(big.Int).Mod(X.X, n)

	return v.Cmp(r) == 0
}
