package curve

import (
	"crypto/rand"
	"math/big"
)

// Point in Jacobian coordinates (X, Y, Z)
// Actual affine point is (X/Z^2, Y/Z^3)
type Point struct {
	X, Y, Z *big.Int
	Curve   *Curve
}

// NewPoint creates an affine point (Z=1)
func NewPoint(x, y *big.Int) *Point {
	return &Point{
		X:     new(big.Int).Set(x),
		Y:     new(big.Int).Set(y),
		Z:     big.NewInt(1),
		Curve: TNM5224,
	}
}

// Infinity returns the point at infinity (0, 1, 0) - wait, Z=0 means infinity usually.
// In our Python implementation: Z=0 is infinity.
func Infinity() *Point {
	return &Point{
		X:     big.NewInt(0),
		Y:     big.NewInt(0), // Can be anything
		Z:     big.NewInt(0),
		Curve: TNM5224,
	}
}

// IsInfinity checks if point is infinity
func (p *Point) IsInfinity() bool {
	return p.Z.Sign() == 0
}

// ToAffine converts Jacobian to Affine coordinates
func (p *Point) ToAffine() *Point {
	if p.IsInfinity() {
		return Infinity()
	}
	if p.Z.Cmp(big.NewInt(1)) == 0 {
		return &Point{X: new(big.Int).Set(p.X), Y: new(big.Int).Set(p.Y), Z: big.NewInt(1), Curve: p.Curve}
	}

	P := p.Curve.P
	zInv := new(big.Int).ModInverse(p.Z, P) // Z^-1
	if zInv == nil {
		// Should not happen if Z != 0 and P is prime
		return Infinity()
	}

	z2 := new(big.Int).Exp(zInv, big.NewInt(2), P) // Z^-2
	z3 := new(big.Int).Mul(z2, zInv)               // Z^-3
	z3.Mod(z3, P)

	x := new(big.Int).Mul(p.X, z2)
	x.Mod(x, P)

	y := new(big.Int).Mul(p.Y, z3)
	y.Mod(y, P)

	return &Point{X: x, Y: y, Z: big.NewInt(1), Curve: p.Curve}
}

// Double doubles the point (2*P) in Jacobian coordinates
// Formulas match Python point.py Double()
func (p *Point) Double() *Point {
	if p.IsInfinity() {
		return Infinity()
	}

	// Constants
	prime := p.Curve.P
	a := p.Curve.A

	X1, Y1, Z1 := p.X, p.Y, p.Z

	// if Y1 == 0 -> Infinity
	if Y1.Sign() == 0 {
		return Infinity()
	}

	// Y1_sq = Y1^2
	Y1_sq := new(big.Int).Mul(Y1, Y1)
	Y1_sq.Mod(Y1_sq, prime)

	// S = 4 * X1 * Y1_sq
	S := new(big.Int).Mul(X1, Y1_sq)
	S.Mul(S, big.NewInt(4))
	S.Mod(S, prime)

	// Z1_sq = Z1^2
	Z1_sq := new(big.Int).Mul(Z1, Z1)
	Z1_sq.Mod(Z1_sq, prime)

	// Z1_4 = Z1_sq^2
	Z1_4 := new(big.Int).Mul(Z1_sq, Z1_sq)
	Z1_4.Mod(Z1_4, prime)

	// M = 3*X1^2 + a*Z1^4
	X1_sq := new(big.Int).Mul(X1, X1)
	M := new(big.Int).Mul(X1_sq, big.NewInt(3))

	AZ1_4 := new(big.Int).Mul(a, Z1_4)
	M.Add(M, AZ1_4)
	M.Mod(M, prime)

	// X3 = M^2 - 2*S
	X3 := new(big.Int).Mul(M, M)
	X3.Sub(X3, new(big.Int).Mul(S, big.NewInt(2)))
	X3.Mod(X3, prime)

	// Y3 = M*(S - X3) - 8*Y1^4
	// Y1_4 = Y1_sq^2
	Y1_4 := new(big.Int).Mul(Y1_sq, Y1_sq)
	Y1_4.Mod(Y1_4, prime)

	Y3_term2 := new(big.Int).Mul(Y1_4, big.NewInt(8))

	Y3 := new(big.Int).Sub(S, X3)
	Y3.Mul(M, Y3)
	Y3.Sub(Y3, Y3_term2)
	Y3.Mod(Y3, prime)

	// Z3 = 2*Y1*Z1
	Z3 := new(big.Int).Mul(Y1, Z1)
	Z3.Mul(Z3, big.NewInt(2))
	Z3.Mod(Z3, prime)

	return &Point{X: X3, Y: Y3, Z: Z3, Curve: p.Curve}
}

// Add adds two points (P + Q)
func (p *Point) Add(q *Point) *Point {
	if p.IsInfinity() {
		return q
	}
	if q.IsInfinity() {
		return p
	}

	prime := p.Curve.P

	X1, Y1, Z1 := p.X, p.Y, p.Z
	X2, Y2, Z2 := q.X, q.Y, q.Z

	// Z1^2, Z2^2
	Z1_sq := new(big.Int).Exp(Z1, big.NewInt(2), prime)
	Z2_sq := new(big.Int).Exp(Z2, big.NewInt(2), prime)

	// U1 = X1 * Z2^2
	U1 := new(big.Int).Mul(X1, Z2_sq)
	U1.Mod(U1, prime)

	// U2 = X2 * Z1^2
	U2 := new(big.Int).Mul(X2, Z1_sq)
	U2.Mod(U2, prime)

	// Z1^3, Z2^3
	Z1_cu := new(big.Int).Mul(Z1_sq, Z1)
	Z1_cu.Mod(Z1_cu, prime)

	Z2_cu := new(big.Int).Mul(Z2_sq, Z2)
	Z2_cu.Mod(Z2_cu, prime)

	// S1 = Y1 * Z2^3
	S1 := new(big.Int).Mul(Y1, Z2_cu)
	S1.Mod(S1, prime)

	// S2 = Y2 * Z1^3
	S2 := new(big.Int).Mul(Y2, Z1_cu)
	S2.Mod(S2, prime)

	if U1.Cmp(U2) == 0 {
		if S1.Cmp(S2) != 0 {
			return Infinity()
		}
		// Same point -> Double
		return p.Double()
	}

	// H = U2 - U1
	H := new(big.Int).Sub(U2, U1)
	H.Mod(H, prime)

	// R = S2 - S1
	R := new(big.Int).Sub(S2, S1)
	R.Mod(R, prime)

	// H^2, H^3
	H_sq := new(big.Int).Mul(H, H)
	H_sq.Mod(H_sq, prime)

	H_cu := new(big.Int).Mul(H_sq, H)
	H_cu.Mod(H_cu, prime)

	// X3 = R^2 - H^3 - 2*U1*H^2
	X3 := new(big.Int).Mul(R, R)
	X3.Sub(X3, H_cu)

	U1H2 := new(big.Int).Mul(U1, H_sq)
	X3.Sub(X3, new(big.Int).Mul(U1H2, big.NewInt(2)))
	X3.Mod(X3, prime)

	// Y3 = R*(U1*H^2 - X3) - S1*H^3
	Y3 := new(big.Int).Sub(U1H2, X3)
	Y3.Mul(R, Y3)

	S1H3 := new(big.Int).Mul(S1, H_cu)
	Y3.Sub(Y3, S1H3)
	Y3.Mod(Y3, prime)

	// Z3 = H * Z1 * Z2
	Z3 := new(big.Int).Mul(H, Z1)
	Z3.Mul(Z3, Z2)
	Z3.Mod(Z3, prime)

	return &Point{X: X3, Y: Y3, Z: Z3, Curve: p.Curve}
}

// ScalarMult multiplies P by coefficient k (k*P) using Montgomery Ladder or Binary exp
// To match Python, we can specific implementations.
// Here we implement basic double-and-add for simplicity or Montgomery if needed.
// Python uses Montgomery Ladder which is safer.
func (p *Point) ScalarMult(k *big.Int) *Point {
	if k.Sign() == 0 || p.IsInfinity() {
		return Infinity()
	}

	R0 := Infinity()
	R1 := p

	// Iterate bits from high to low
	// Using basic double-and-add for readability first
	// Or Montgomery ladder:
	// R0 = 0, R1 = P
	// for i down to 0:
	//   if bit == 0: R1 = R0+R1; R0 = 2R0
	//   else: R0 = R0+R1; R1 = 2R1

	// Let's rely on Double and Add
	// This Montgomery implementation matches Python
	bitLen := k.BitLen()

	// Need copies to avoid mutating original P if pointer shared
	// But our Add/Double return new Points, so safe.
	currR0 := R0
	currR1 := R1

	for i := bitLen - 1; i >= 0; i-- {
		bit := k.Bit(i)
		if bit == 0 {
			currR1 = currR0.Add(currR1)
			currR0 = currR0.Double()
		} else {
			currR0 = currR0.Add(currR1)
			currR1 = currR1.Double()
		}
	}

	return currR0.ToAffine()
}

// GenerateBasePoint returns G
func GenerateBasePoint() *Point {
	return NewPoint(TNM5224.Gx, TNM5224.Gy)
}

// GenerateRandomKey generates a private key
func GenerateRandomKey() (*big.Int, error) {
	n := TNM5224.N
	// k in [1, n-1]
	k, err := rand.Int(rand.Reader, new(big.Int).Sub(n, big.NewInt(1)))
	if err != nil {
		return nil, err
	}
	k.Add(k, big.NewInt(1))
	return k, nil
}
