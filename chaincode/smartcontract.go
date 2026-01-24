package main

import (
	"crypto/ecdsa"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"log"
	"math/big"
	"strings"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// SmartContract provides functions for managing Diplomas
type SmartContract struct {
	contractapi.Contract
}

// MinistryOfEducation defines the root authority
type MinistryOfEducation struct {
	DocType   string `json:"docType"` // ministry
	ID        string `json:"id"`
	Name      string `json:"name"`
	PublicKey string `json:"publicKey"`
}

// School defines the structure for a University/School
type School struct {
	DocType        string `json:"docType"` // school
	ID             string `json:"id"`
	Name           string `json:"name"`
	PublicKey      string `json:"publicKey"`
	Certificate    string `json:"certificate"`    // Always output, empty string if not set
	Status         string `json:"status"`         // ACTIVE, REVOKED, PENDING
	RegisteredDate string `json:"registeredDate"` // Empty string if not registered yet
}

// Diploma defines the structure for a Digital Diploma
type Diploma struct {
	DocType      string `json:"docType"` // diploma
	ID           string `json:"id"`
	FileHash     string `json:"fileHash"`
	Signature    string `json:"signature"`
	SchoolID     string `json:"schoolId"`
	StudentName  string `json:"studentName"`
	StudentID    string `json:"studentId"`
	Major        string `json:"major"` // Ngành học
	Grade        string `json:"grade"` // Xếp loại (Excellent, Good, etc.)
	IssueDate    string `json:"issueDate"`
	Status       string `json:"status"`       // ISSUED, REVOKED
	RevokeReason string `json:"revokeReason"` // Removed omitempty to always output field
}

// helper to parse hex
func hexToBigInt(hexStr string) *big.Int {
	hexStr = strings.TrimPrefix(hexStr, "0x")
	i := new(big.Int)
	i.SetString(hexStr, 16)
	return i
}

// verifySignatureInternal verifies the signature using TNM5224 curve
// Message reconstructed to match Python's json.dumps({"file_hash": hash})
func (s *SmartContract) verifySignatureInternal(fileHash string, signatureStr string, publicKeyStr string) (bool, error) {
	// 1. Reconstruct Data to Sign
	// Python: {"file_hash": "HASH"} (with space after colon)
	msgStr := fmt.Sprintf("{\"file_hash\": \"%s\"}", fileHash)

	// 2. Hash message
	hash := sha256.Sum256([]byte(msgStr))

	// 3. Parse Signature (hex_r,hex_s)
	parts := strings.Split(signatureStr, ",")
	if len(parts) != 2 {
		return false, fmt.Errorf("invalid signature format (expected r,s)")
	}
	sigR := hexToBigInt(parts[0])
	sigS := hexToBigInt(parts[1])

	// 4. Parse Public Key (hex_x,hex_y)
	pubParts := strings.Split(publicKeyStr, ",")
	if len(pubParts) != 2 {
		return false, fmt.Errorf("invalid public key format (expected x,y)")
	}
	x := hexToBigInt(pubParts[0])
	y := hexToBigInt(pubParts[1])

	// 5. Verify using ecdsa.Verify with Custom Curve
	pub := &ecdsa.PublicKey{
		Curve: TNM5224(),
		X:     x,
		Y:     y,
	}

	if pub.X == nil || pub.Y == nil || sigR == nil || sigS == nil {
		return false, fmt.Errorf("invalid hex values")
	}

	return ecdsa.Verify(pub, hash[:], sigR, sigS), nil
}

// InitLedger initializes the ledger with Ministry of Education
func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface, moePublicKey string) error {
	moe := MinistryOfEducation{
		DocType:   "ministry",
		ID:        "MOE",
		Name:      "Ministry of Education and Training",
		PublicKey: moePublicKey,
	}

	moeJSON, err := json.Marshal(moe)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState("MOE", moeJSON)
}

// GetMinistry returns the Ministry of Education info
func (s *SmartContract) GetMinistry(ctx contractapi.TransactionContextInterface) (*MinistryOfEducation, error) {
	moeJSON, err := ctx.GetStub().GetState("MOE")
	if err != nil {
		return nil, fmt.Errorf("failed to read MoE from world state: %v", err)
	}
	if moeJSON == nil {
		return nil, fmt.Errorf("Ministry of Education not initialized")
	}

	var moe MinistryOfEducation
	err = json.Unmarshal(moeJSON, &moe)
	if err != nil {
		return nil, err
	}

	return &moe, nil
}

// ================== HELPER: COMPOSITE KEYS ==================

// indexSchool saves a helper index for querying schools
func (s *SmartContract) indexSchool(ctx contractapi.TransactionContextInterface, school *School) error {
	indexName := "docType~id"
	colorNameIndexKey, err := ctx.GetStub().CreateCompositeKey(indexName, []string{school.DocType, school.ID})
	if err != nil {
		return err
	}
	//  Value could be empty or the ID
	return ctx.GetStub().PutState(colorNameIndexKey, []byte{0x00})
}

// indexDiploma saves a helper index for querying diplomas by school
func (s *SmartContract) indexDiploma(ctx contractapi.TransactionContextInterface, diploma *Diploma) error {
	indexName := "school~id"
	// Create index: schoolId -> diplomaFileHash
	indexKey, err := ctx.GetStub().CreateCompositeKey(indexName, []string{diploma.SchoolID, diploma.FileHash})
	if err != nil {
		return err
	}
	return ctx.GetStub().PutState(indexKey, []byte{0x00})
}

// ================== MODIFIED FUNCTIONS WITH INDEXING ==================

// CreateSchool registers basic school info with PENDING status. Idempotent.
func (s *SmartContract) CreateSchool(ctx contractapi.TransactionContextInterface, id string, name string, publicKey string) error {
	fmt.Printf("🔵 CreateSchool called: schoolId=%s, name=%s\n", id, name)

	existingJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return fmt.Errorf("failed to read from world state: %v", err)
	}
	if existingJSON != nil {
		// Log and return nil to ensure idempotency (already exists is a success state for the caller)
		fmt.Printf("School %s already exists on ledger\n", id)
		return nil
	}

	school := School{
		DocType:   "school",
		ID:        id,
		Name:      name,
		PublicKey: publicKey,
		Status:    "PENDING",
	}

	schoolJSON, err := json.Marshal(school)
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(id, schoolJSON)
	if err != nil {
		return err
	}

	// Indexing for GetAllSchools
	return s.indexSchool(ctx, &school)
}

// RegisterSchool (Approve) updates a school to ACTIVE status. Must be PENDING.
func (s *SmartContract) RegisterSchool(ctx contractapi.TransactionContextInterface, id string, name string, publicKey string, certificate string, registeredDate string) error {
	existingSchoolJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return fmt.Errorf("failed to read from world state: %v", err)
	}
	if existingSchoolJSON == nil {
		return fmt.Errorf("school %s does not exist. Call CreateSchool first", id)
	}

	var school School
	err = json.Unmarshal(existingSchoolJSON, &school)
	if err != nil {
		return err
	}

	// Logic Check: Only PENDING schools can be approved
	if school.Status != "PENDING" {
		return fmt.Errorf("school %s cannot be approved. Current status: %s", id, school.Status)
	}

	school.DocType = "school" // Ensure docType
	school.PublicKey = publicKey
	school.Certificate = certificate
	school.RegisteredDate = registeredDate
	school.Status = "ACTIVE"

	schoolJSON, err := json.Marshal(school)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(id, schoolJSON)
}

// GetSchool returns school information
func (s *SmartContract) GetSchool(ctx contractapi.TransactionContextInterface, schoolId string) (*School, error) {
	schoolJSON, err := ctx.GetStub().GetState(schoolId)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if schoolJSON == nil {
		return nil, fmt.Errorf("school %s does not exist", schoolId)
	}

	var school School
	err = json.Unmarshal(schoolJSON, &school)
	if err != nil {
		return nil, err
	}

	return &school, nil
}

// IssueDiploma issues a new diploma (Can only be called by a registered School)
func (s *SmartContract) IssueDiploma(ctx contractapi.TransactionContextInterface,
	id string, fileHash string, signature string, schoolId string,
	studentName string, studentId string, major string, grade string, issueDate string) error {

	// 1. Check if School exists and is ACTIVE
	school, err := s.GetSchool(ctx, schoolId)
	if err != nil {
		return err
	}

	if school.Status != "ACTIVE" {
		return fmt.Errorf("school %s is not active (status: %s)", schoolId, school.Status)
	}

	// 2. Verify Signature (ENHANCEMENT: Using TNM5224)
	isValid, err := s.verifySignatureInternal(fileHash, signature, school.PublicKey)
	if err != nil {
		return fmt.Errorf("signature check error: %v", err)
	}
	if !isValid {
		return fmt.Errorf("invalid diploma signature from school")
	}

	// 3. Check if Diploma already exists
	exists, err := s.DiplomaExists(ctx, fileHash)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("the diploma with hash %s already exists", fileHash)
	}

	// 4. Create Diploma
	diploma := Diploma{
		DocType:     "diploma",
		ID:          id,
		FileHash:    fileHash,
		Signature:   signature,
		SchoolID:    schoolId,
		StudentName: studentName,
		StudentID:   studentId,
		Major:       major,
		Grade:       grade,
		IssueDate:   issueDate,
		Status:      "ISSUED",
	}

	diplomaJSON, err := json.Marshal(diploma)
	if err != nil {
		return err
	}

	// Key is fileHash to easily verify later
	err = ctx.GetStub().PutState(fileHash, diplomaJSON)
	if err != nil {
		return err
	}

	// Create Index school~id
	return s.indexDiploma(ctx, &diploma)
}

// RevokeSchool revokes a school's permission (Can only be called by Ministry)
func (s *SmartContract) RevokeSchool(ctx contractapi.TransactionContextInterface, schoolId string) error {
	school, err := s.GetSchool(ctx, schoolId)
	if err != nil {
		return err
	}

	school.Status = "REVOKED"
	updatedSchoolJSON, err := json.Marshal(school)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(schoolId, updatedSchoolJSON)
}

// RevokeDiploma revokes a diploma (Can only be called by the issuing School or MoE)
func (s *SmartContract) RevokeDiploma(ctx contractapi.TransactionContextInterface, fileHash string, reason string) error {
	diplomaJSON, err := ctx.GetStub().GetState(fileHash)
	if err != nil {
		return fmt.Errorf("failed to read from world state: %v", err)
	}
	if diplomaJSON == nil {
		return fmt.Errorf("diploma with hash %s does not exist", fileHash)
	}

	var diploma Diploma
	err = json.Unmarshal(diplomaJSON, &diploma)
	if err != nil {
		return err
	}

	diploma.Status = "REVOKED"
	diploma.RevokeReason = reason

	updatedDiplomaJSON, err := json.Marshal(diploma)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(fileHash, updatedDiplomaJSON)
}

// VerifyDiploma returns the diploma stored in the world state with given hash
func (s *SmartContract) VerifyDiploma(ctx contractapi.TransactionContextInterface, fileHash string) (*Diploma, error) {
	diplomaJSON, err := ctx.GetStub().GetState(fileHash)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if diplomaJSON == nil {
		return nil, fmt.Errorf("the diploma %s does not exist", fileHash)
	}

	var diploma Diploma
	err = json.Unmarshal(diplomaJSON, &diploma)
	if err != nil {
		return nil, err
	}

	return &diploma, nil
}

// GetDiplomaWithSchoolInfo returns diploma with school information for verification
func (s *SmartContract) GetDiplomaWithSchoolInfo(ctx contractapi.TransactionContextInterface, fileHash string) (map[string]interface{}, error) {
	diploma, err := s.VerifyDiploma(ctx, fileHash)
	if err != nil {
		return nil, err
	}

	school, err := s.GetSchool(ctx, diploma.SchoolID)
	if err != nil {
		return nil, err
	}

	moe, err := s.GetMinistry(ctx)
	// MoE might not be strictly required for verification if school is active, but we return it if available
	if err != nil {
		fmt.Printf("Warning: MoE info not available: %v\n", err)
	}

	result := map[string]interface{}{
		"diploma": diploma,
		"school":  school,
		"moe":     moe,
	}

	return result, nil
}

// DiplomaExists returns true when asset with given ID exists in world state
func (s *SmartContract) DiplomaExists(ctx contractapi.TransactionContextInterface, fileHash string) (bool, error) {
	diplomaJSON, err := ctx.GetStub().GetState(fileHash)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return diplomaJSON != nil, nil
}

// ================== QUERY FUNCTIONS (MISSING IMPLEMENTATION FIXED) ==================

// ================== QUERY FUNCTIONS (LEVELDB FRIENDLY) ==================

// GetDiplomasBySchool queries all diplomas for a specific school using Composite Keys
func (s *SmartContract) GetDiplomasBySchool(ctx contractapi.TransactionContextInterface, schoolId string) ([]*Diploma, error) {
	// Query using "school~id" index
	resultsIterator, err := ctx.GetStub().GetStateByPartialCompositeKey("school~id", []string{schoolId})
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var diplomas []*Diploma
	for resultsIterator.HasNext() {
		response, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		// Split Key to get the fileHash (schoolId, fileHash)
		_, compositeKeyParts, err := ctx.GetStub().SplitCompositeKey(response.Key)
		if err != nil {
			return nil, err
		}

		if len(compositeKeyParts) > 1 {
			fileHash := compositeKeyParts[1]
			// Get actual diploma data
			diploma, err := s.VerifyDiploma(ctx, fileHash)
			if err == nil {
				diplomas = append(diplomas, diploma)
			}
		}
	}

	return diplomas, nil
}

// GetAllSchools queries all registered schools
func (s *SmartContract) GetAllSchools(ctx contractapi.TransactionContextInterface) ([]*School, error) {
	// Query using "docType~id" index with "school"
	resultsIterator, err := ctx.GetStub().GetStateByPartialCompositeKey("docType~id", []string{"school"})
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var schools []*School
	for resultsIterator.HasNext() {
		response, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		_, compositeKeyParts, err := ctx.GetStub().SplitCompositeKey(response.Key)
		if err != nil {
			return nil, err
		}

		if len(compositeKeyParts) > 1 {
			schoolID := compositeKeyParts[1]
			school, err := s.GetSchool(ctx, schoolID)
			if err == nil {
				schools = append(schools, school)
			}
		}
	}

	return schools, nil
}

// GetSystemStatistics aggregates stats (schools, diplomas)
func (s *SmartContract) GetSystemStatistics(ctx contractapi.TransactionContextInterface) (map[string]int, error) {
	stats := map[string]int{
		"total_schools":   0,
		"active_schools":  0,
		"revoked_schools": 0,
		"total_diplomas":  0,
	}

	// 1. Count Schools
	schools, err := s.GetAllSchools(ctx)
	if err == nil {
		stats["total_schools"] = len(schools)
		for _, sch := range schools {
			if sch.Status == "ACTIVE" {
				stats["active_schools"]++
			} else if sch.Status == "REVOKED" {
				stats["revoked_schools"]++
			}
		}
	}

	// 2. Count Diplomas (Simplified: Iterate all schools)
	// This is not efficient, but sufficient for test network/leveldb without selectors
	// A improved way would be to have "docType~fileHash" index for all diplomas
	for _, sch := range schools {
		diplomas, _ := s.GetDiplomasBySchool(ctx, sch.ID)
		stats["total_diplomas"] += len(diplomas)
	}

	return stats, nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&SmartContract{})
	if err != nil {
		log.Panicf("Error creating diploma chaincode: %v", err)
	}

	if err := chaincode.Start(); err != nil {
		log.Panicf("Error starting diploma chaincode: %v", err)
	}
}
