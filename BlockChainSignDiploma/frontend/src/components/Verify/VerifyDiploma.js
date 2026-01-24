import React, { useState } from 'react';
import { Container, Card, Button, Alert, Form, Badge, Spinner } from 'react-bootstrap';
import { FaCheckCircle, FaTimesCircle, FaFileUpload, FaSearch } from 'react-icons/fa';
import { verifyAPI } from '../../services/api';
import { formatDate, truncateHash } from '../../utils/helpers';

const VerifyDiploma = () => {
  const [file, setFile] = useState(null);
  const [fileHash, setFileHash] = useState('');
  const [verifyMode, setVerifyMode] = useState('file'); // 'file' or 'hash'
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
    setResult(null);
  };

  const handleVerifyByFile = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('pdf_file', file);

      const response = await verifyAPI.verifyByFile(formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyByHash = async (e) => {
    e.preventDefault();
    if (!fileHash.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await verifyAPI.verifyByHash(fileHash.trim());
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  const renderVerificationChecks = () => {
    if (!result?.verification_checks) return null;

    const checks = [
      {
        key: 'exists_on_blockchain',
        label: 'Exists on Blockchain',
        description: 'Diploma is recorded on blockchain',
      },
      {
        key: 'not_revoked',
        label: 'Not Revoked',
        description: 'Diploma has not been revoked',
      },
      {
        key: 'school_is_active',
        label: 'School is Active',
        description: 'Issuing school is authorized',
      },
      {
        key: 'signature_valid',
        label: 'Signature Valid',
        description: 'Digital signature is authentic',
      },
    ];

    return (
      <Card className="mt-4">
        <Card.Header>
          <h6 className="mb-0">Security Checks (4 Layers)</h6>
        </Card.Header>
        <Card.Body>
          {checks.map((check) => {
            const value = result.verification_checks[check.key];
            return (
              <div key={check.key} className="d-flex align-items-center mb-3">
                {value === true ? (
                  <FaCheckCircle className="text-success me-3" size={24} />
                ) : value === false ? (
                  <FaTimesCircle className="text-danger me-3" size={24} />
                ) : (
                  <FaTimesCircle className="text-muted me-3" size={24} />
                )}
                <div>
                  <div className="fw-bold">{check.label}</div>
                  <small className="text-muted">{check.description}</small>
                </div>
              </div>
            );
          })}
        </Card.Body>
      </Card>
    );
  };

  return (
    <Container className="py-5">
      <h2 className="text-center mb-4 fw-bold">
        <FaCheckCircle className="me-2" />
        Verify Diploma
      </h2>
      <p className="text-center text-muted mb-5">
        Verify the authenticity of a diploma using file or hash
      </p>

      <div className="row justify-content-center">
        <div className="col-lg-8">
          {/* Mode Selection */}
          <div className="btn-group w-100 mb-4" role="group">
            <button
              type="button"
              className={`btn ${verifyMode === 'file' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setVerifyMode('file')}
            >
              <FaFileUpload className="me-2" />
              Verify by File
            </button>
            <button
              type="button"
              className={`btn ${verifyMode === 'hash' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setVerifyMode('hash')}
            >
              <FaSearch className="me-2" />
              Verify by Hash
            </button>
          </div>

          {/* Verification Form */}
          <Card className="shadow-sm mb-4">
            <Card.Body className="p-4">
              {verifyMode === 'file' ? (
                <Form onSubmit={handleVerifyByFile}>
                  <Form.Group className="mb-3">
                    <Form.Label className="fw-bold">Upload Diploma PDF</Form.Label>
                    <Form.Control
                      type="file"
                      accept=".pdf"
                      onChange={handleFileChange}
                      required
                    />
                    <Form.Text className="text-muted">
                      Select the diploma PDF file to verify
                    </Form.Text>
                  </Form.Group>

                  {file && (
                    <Alert variant="info">
                      <strong>Selected:</strong> {file.name} ({(file.size / 1024).toFixed(2)} KB)
                    </Alert>
                  )}

                  <Button
                    variant="primary"
                    type="submit"
                    className="w-100"
                    disabled={!file || loading}
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Verifying...
                      </>
                    ) : (
                      <>
                        <FaCheckCircle className="me-2" />
                        Verify Diploma
                      </>
                    )}
                  </Button>
                </Form>
              ) : (
                <Form onSubmit={handleVerifyByHash}>
                  <Form.Group className="mb-3">
                    <Form.Label className="fw-bold">Enter File Hash</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="Enter SHA-256 hash of the diploma"
                      value={fileHash}
                      onChange={(e) => setFileHash(e.target.value)}
                      required
                      className="font-monospace"
                    />
                    <Form.Text className="text-muted">
                      64-character hexadecimal hash
                    </Form.Text>
                  </Form.Group>

                  <Button
                    variant="primary"
                    type="submit"
                    className="w-100"
                    disabled={!fileHash.trim() || loading}
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Verifying...
                      </>
                    ) : (
                      <>
                        <FaSearch className="me-2" />
                        Verify by Hash
                      </>
                    )}
                  </Button>
                </Form>
              )}
            </Card.Body>
          </Card>

          {/* Error Message */}
          {error && <Alert variant="danger">{error}</Alert>}

          {/* Verification Result */}
          {result && (
            <div>
              {/* Main Result */}
              <Alert variant={result.is_valid ? 'success' : 'danger'} className="text-center">
                <div className="display-1 mb-3">
                  {result.is_valid ? <FaCheckCircle /> : <FaTimesCircle />}
                </div>
                <h3 className="fw-bold">
                  {result.is_valid ? '✅ VALID DIPLOMA' : '❌ INVALID DIPLOMA'}
                </h3>
                <p className="mb-0">{result.verification_result}</p>
              </Alert>

              {/* File Hash */}
              <Card className="mb-3">
                <Card.Body>
                  <strong>File Hash:</strong>
                  <div className="font-monospace small text-break mt-2">{result.file_hash}</div>
                </Card.Body>
              </Card>

              {/* Verification Checks */}
              {renderVerificationChecks()}

              {/* Diploma Info */}
              {result.diploma_info && (
                <Card className="mt-3">
                  <Card.Header className="bg-info text-white">
                    <h6 className="mb-0">Diploma Information</h6>
                  </Card.Header>
                  <Card.Body>
                    <div className="row">
                      <div className="col-md-6 mb-3">
                        <strong>Diploma ID:</strong>
                        <div>{result.diploma_info.diplomaId}</div>
                      </div>
                      <div className="col-md-6 mb-3">
                        <strong>Status:</strong>
                        <div>
                          <Badge bg={result.diploma_info.status === 'ACTIVE' ? 'success' : 'danger'}>
                            {result.diploma_info.status}
                          </Badge>
                        </div>
                      </div>
                      <div className="col-md-6 mb-3">
                        <strong>Student Name:</strong>
                        <div>{result.diploma_info.studentName}</div>
                      </div>
                      <div className="col-md-6 mb-3">
                        <strong>Student ID:</strong>
                        <div>{result.diploma_info.studentId}</div>
                      </div>
                      <div className="col-md-6 mb-3">
                        <strong>Major:</strong>
                        <div>{result.diploma_info.major}</div>
                      </div>
                      <div className="col-md-6 mb-3">
                        <strong>Grade:</strong>
                        <div>
                          <Badge bg="primary">{result.diploma_info.grade}</Badge>
                        </div>
                      </div>
                      <div className="col-md-6 mb-3">
                        <strong>Issue Date:</strong>
                        <div>{result.diploma_info.issueDate}</div>
                      </div>
                    </div>

                    {result.diploma_info.revokedAt && (
                      <Alert variant="danger" className="mt-3">
                        <strong>⚠️ Revoked:</strong> {formatDate(result.diploma_info.revokedAt)}
                        <br />
                        <strong>Reason:</strong> {result.diploma_info.reason}
                      </Alert>
                    )}
                  </Card.Body>
                </Card>
              )}

              {/* School Info */}
              {result.school_info && (
                <Card className="mt-3">
                  <Card.Header className="bg-success text-white">
                    <h6 className="mb-0">School Information</h6>
                  </Card.Header>
                  <Card.Body>
                    <div className="row">
                      <div className="col-md-6 mb-3">
                        <strong>School ID:</strong>
                        <div>{result.school_info.schoolId}</div>
                      </div>
                      <div className="col-md-6 mb-3">
                        <strong>School Name:</strong>
                        <div>{result.school_info.schoolName}</div>
                      </div>
                      <div className="col-md-6 mb-3">
                        <strong>Status:</strong>
                        <div>
                          <Badge bg={result.school_info.status === 'ACTIVE' ? 'success' : 'danger'}>
                            {result.school_info.status}
                          </Badge>
                        </div>
                      </div>
                      <div className="col-md-6 mb-3">
                        <strong>Registered Date:</strong>
                        <div>{result.school_info.registeredDate}</div>
                      </div>
                    </div>
                  </Card.Body>
                </Card>
              )}

              {/* Signature Verification */}
              {result.signature_verification && (
                <Card className="mt-3">
                  <Card.Header>
                    <h6 className="mb-0">Digital Signature</h6>
                  </Card.Header>
                  <Card.Body>
                    <div className="mb-2">
                      <strong>Algorithm:</strong> {result.signature_verification.algorithm}
                    </div>
                    <div className="mb-2">
                      <strong>Verified With:</strong> {result.signature_verification.verified_with}
                    </div>
                    <div>
                      <strong>Valid:</strong>{' '}
                      {result.signature_verification.is_valid ? (
                        <Badge bg="success">Yes</Badge>
                      ) : (
                        <Badge bg="danger">No</Badge>
                      )}
                    </div>
                  </Card.Body>
                </Card>
              )}

              {/* Blockchain Info */}
              {result.blockchain_tx && (
                <Card className="mt-3">
                  <Card.Body>
                    <strong>Blockchain Transaction:</strong>
                    <div className="font-monospace small text-break mt-2">
                      {result.blockchain_tx}
                    </div>
                  </Card.Body>
                </Card>
              )}

              <Alert variant="info" className="mt-3">
                <small>
                  <strong>Verified at:</strong> {formatDate(result.verified_at || new Date().toISOString())}
                </small>
              </Alert>
            </div>
          )}
        </div>
      </div>
    </Container>
  );
};

export default VerifyDiploma;
