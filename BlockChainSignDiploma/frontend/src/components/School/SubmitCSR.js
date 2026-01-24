import React, { useState, useEffect } from 'react';
import { Container, Card, Form, Button, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { FaFileAlt } from 'react-icons/fa';
import { useAuth } from '../../contexts/AuthContext';
import { csrAPI } from '../../services/api';
import SuccessModal from '../Common/SuccessModal';

const SubmitCSR = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    schoolId: user?.schoolId || '',
    schoolName: user?.schoolName || '',
    publicKey: '',
    csrSignature: '',
    email: user?.email || '',
    address: '',
    taxCode: '',
    legalRepresentative: '',
    phone: '',
    verificationFile: null,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [csrExists, setCsrExists] = useState(false);
  const [rejectedReason, setRejectedReason] = useState(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);

  useEffect(() => {
    checkCSRStatus();
  }, []);

  const checkCSRStatus = async () => {
    try {
      const response = await csrAPI.getStatus();
      const csr = response.data.data?.csr;

      if (csr) {
        if (['PENDING', 'APPROVED', 'REVOKED'].includes(csr.status)) {
          setCsrExists(true);
        } else if (csr.status === 'REJECTED') {
          setRejectedReason(csr.rejectionReason || 'Your previous request was rejected.');
        }
      }
    } catch (error) {
      console.error('Error checking CSR status:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData({
      ...formData,
      [name]: files ? files[0] : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const submitData = new FormData();
      Object.keys(formData).forEach((key) => {
        submitData.append(key, formData[key]);
      });

      await csrAPI.submit(submitData);

      // Show success modal
      setShowSuccessModal(true);

      // Auto dismiss and redirect
      setTimeout(() => {
        setShowSuccessModal(false);
        navigate('/school/dashboard');
      }, 1500);

    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit CSR');
    } finally {
      setLoading(false);
    }
  };

  if (csrExists) {
    return (
      <Container className="py-5">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <Alert variant="info">
              <h4>CSR Already Submitted</h4>
              <p>You have already submitted a CSR. Please check your dashboard for status.</p>
              <Button variant="primary" onClick={() => navigate('/school/dashboard')}>
                Go to Dashboard
              </Button>
            </Alert>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container className="py-5">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <Card className="shadow-sm">
            <Card.Header className="bg-primary text-white">
              <h4 className="mb-0">
                <FaFileAlt className="me-2" />
                Submit Certificate Signing Request (CSR)
              </h4>
            </Card.Header>
            <Card.Body className="p-4">
              {error && <Alert variant="danger">{error}</Alert>}

              {rejectedReason && (
                <Alert variant="danger" className="mb-4 text-center">
                  <h5 className="alert-heading text-danger fw-bold">Your Previous CSR was Rejected</h5>
                  <p className="mb-0">Reason: <strong>{rejectedReason}</strong></p>
                  <hr />
                  <p className="mb-0 small">Please review your information and submit a new request.</p>
                </Alert>
              )}

              <Alert variant="info" className="mb-4">
                <strong>CSR Verification Process (Proof of Possession):</strong>
                <ol className="mb-0 mt-2 ps-3">
                  <li>Generate a keypair using <a href="/crypto-tools" target="_blank">Crypto Tools</a> (if you haven't already).</li>
                  <li>Create a simple file (e.g., a text file with your School Name).</li>
                  <li>Use the <a href="/sign-file" target="_blank">Sign File Tool</a> to sign this file with your Private Key.</li>
                  <li>Upload the file below and paste the generated signature.</li>
                  <li>This proves you possess the Private Key corresponding to the Public Key you are submitting.</li>
                </ol>
              </Alert>

              <Form onSubmit={handleSubmit}>
                <h5 className="mb-3">School Information</h5>

                <Form.Group className="mb-3">
                  <Form.Label>School ID *</Form.Label>
                  <Form.Control
                    type="text"
                    name="schoolId"
                    value={formData.schoolId}
                    onChange={handleChange}
                    required
                    readOnly
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>School Name *</Form.Label>
                  <Form.Control
                    type="text"
                    name="schoolName"
                    value={formData.schoolName}
                    onChange={handleChange}
                    required
                    readOnly
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Email *</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    readOnly
                  />
                </Form.Group>

                <hr className="my-4" />

                <h5 className="mb-3">Cryptographic Keys & Verification</h5>

                <Form.Group className="mb-3">
                  <Form.Label>Public Key * (Format: 0xX,0xY)</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={2}
                    name="publicKey"
                    value={formData.publicKey}
                    onChange={handleChange}
                    placeholder="0x1234...,0x5678..."
                    required
                    className="font-monospace small"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Verification File * (The file you signed)</Form.Label>
                  <Form.Control
                    type="file"
                    name="verificationFile"
                    onChange={handleChange}
                    required
                  />
                  <Form.Text className="text-muted">
                    Upload the exact file used to generate the signature below.
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>CSR Signature * (Signature of the file above)</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="csrSignature"
                    value={formData.csrSignature}
                    onChange={handleChange}
                    placeholder="0xabcd...,0xef01..."
                    required
                    className="font-monospace small"
                  />
                  <Form.Text className="text-muted">
                    Paste the signature generated by signing the verification file.
                  </Form.Text>
                </Form.Group>

                <hr className="my-4" />

                <h5 className="mb-3">Additional Information (Optional)</h5>

                <Form.Group className="mb-3">
                  <Form.Label>Address</Form.Label>
                  <Form.Control
                    type="text"
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    placeholder="Full address"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Tax Code</Form.Label>
                  <Form.Control
                    type="text"
                    name="taxCode"
                    value={formData.taxCode}
                    onChange={handleChange}
                    placeholder="Tax identification number"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Legal Representative</Form.Label>
                  <Form.Control
                    type="text"
                    name="legalRepresentative"
                    value={formData.legalRepresentative}
                    onChange={handleChange}
                    placeholder="Name of legal representative"
                  />
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>Phone</Form.Label>
                  <Form.Control
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    placeholder="Contact phone number"
                  />
                </Form.Group>

                <div className="d-grid gap-2">
                  <Button
                    variant="primary"
                    type="submit"
                    size="lg"
                    disabled={loading || showSuccessModal}
                  >
                    {loading ? 'Submitting...' : 'Submit CSR'}
                  </Button>
                  <Button
                    variant="outline-secondary"
                    onClick={() => navigate('/school/dashboard')}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </div>
      </div>

      {/* Success Modal */}
      <SuccessModal
        show={showSuccessModal}
        onHide={() => { }} // No closing by user, wait for redirect
        title="CSR Submitted!"
        message="Your Certificate Signing Request has been submitted successfully. Waiting for Ministry approval."
        autoDismiss={true}
      />
    </Container>
  );
};

export default SubmitCSR;
