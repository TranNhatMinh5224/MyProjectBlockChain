import React, { useState } from 'react';
import { Container, Card, Button, Alert, Form, Badge } from 'react-bootstrap';
import { FaSignature, FaFileUpload, FaKey, FaCopy, FaCheckCircle } from 'react-icons/fa';
import { cryptoAPI } from '../../services/api';
import { copyToClipboard, truncateHash } from '../../utils/helpers';

const SignFile = () => {
  const [formData, setFormData] = useState({
    file: null,
    private_key: ''
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState({ hash: false, signature: false, publicKey: false });

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFormData({ ...formData, file });
    setResult(null);
    setError('');
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSignFile = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      if (!formData.file) {
        throw new Error('Please select a file');
      }
      if (!formData.private_key) {
        throw new Error('Please enter your private key');
      }

      const signFormData = new FormData();
      signFormData.append('file', formData.file);
      signFormData.append('private_key', formData.private_key);

      const response = await cryptoAPI.signFile(signFormData);
      setResult(response.data.data);
    } catch (err) {
      setError(err.message || err.response?.data?.detail || 'Failed to sign file');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text, type) => {
    if (copyToClipboard(text)) {
      setCopied({ ...copied, [type]: true });
      setTimeout(() => setCopied({ ...copied, [type]: false }), 2000);
    }
  };

  return (
    <Container className="py-5">
      <div className="text-center mb-5">
        <h2 className="fw-bold">
          <FaSignature className="me-2 text-primary" />
          Sign File
        </h2>
        <p className="text-muted">
          Sign any file with your private key using TNM5224 Elliptic Curve Digital Signature
        </p>
        <Badge bg="info" className="mb-2">Public Tool - No Login Required</Badge>
      </div>

      <div className="row justify-content-center">
        <div className="col-lg-8">
          {/* Sign File Form */}
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-primary text-white">
              <h5 className="mb-0">
                <FaFileUpload className="me-2" />
                Upload File & Sign
              </h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleSignFile}>
                {/* File Upload */}
                <Form.Group className="mb-4">
                  <Form.Label className="fw-bold">
                    Select File to Sign *
                  </Form.Label>
                  <Form.Control
                    type="file"
                    onChange={handleFileChange}
                    required
                    accept=".pdf,.docx,.doc,.txt"
                  />
                  <Form.Text className="text-muted">
                    Supported formats: PDF, DOCX, DOC, TXT
                  </Form.Text>
                  {formData.file && (
                    <Alert variant="info" className="mt-2 mb-0">
                      <FaCheckCircle className="me-2" />
                      Selected: <strong>{formData.file.name}</strong> ({(formData.file.size / 1024).toFixed(2)} KB)
                    </Alert>
                  )}
                </Form.Group>

                {/* Private Key Input */}
                <Form.Group className="mb-4">
                  <Form.Label className="fw-bold text-danger">
                    <FaKey className="me-2" />
                    Your Private Key *
                  </Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="private_key"
                    value={formData.private_key}
                    onChange={handleInputChange}
                    placeholder="0x1234567890abcdef..."
                    required
                    className="font-monospace small"
                  />
                  <Form.Text className="text-muted">
                    Enter your private key in hex format (starts with 0x). 
                    Don't have a keypair? <a href="/crypto-tools">Generate one here</a>.
                  </Form.Text>
                </Form.Group>

                {error && <Alert variant="danger">{error}</Alert>}

                {/* Submit Button */}
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  disabled={loading || !formData.file || !formData.private_key}
                  className="w-100"
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" />
                      Signing...
                    </>
                  ) : (
                    <>
                      <FaSignature className="me-2" />
                      Sign File
                    </>
                  )}
                </Button>
              </Form>
            </Card.Body>
          </Card>

          {/* Result Card */}
          {result && (
            <Card className="shadow-sm border-success">
              <Card.Header className="bg-success text-white">
                <h5 className="mb-0">
                  <FaCheckCircle className="me-2" />
                  Signature Generated Successfully!
                </h5>
              </Card.Header>
              <Card.Body>
                <Alert variant="success">
                  ✅ Your file has been signed successfully! You can now use this signature to verify the file's authenticity.
                </Alert>

                {/* File Hash */}
                <Form.Group className="mb-4">
                  <Form.Label className="fw-bold text-primary">
                    📄 File Hash (SHA-256)
                  </Form.Label>
                  <div className="d-flex gap-2">
                    <Form.Control
                      value={result.file_hash}
                      readOnly
                      className="font-monospace small"
                    />
                    <Button
                      variant="outline-primary"
                      onClick={() => handleCopy(result.file_hash, 'hash')}
                      style={{ minWidth: '100px' }}
                    >
                      <FaCopy /> {copied.hash ? 'Copied!' : 'Copy'}
                    </Button>
                  </div>
                  <Form.Text className="text-muted">
                    This is the unique fingerprint of your file
                  </Form.Text>
                </Form.Group>

                {/* Signature */}
                <Form.Group className="mb-4">
                  <Form.Label className="fw-bold text-success">
                    ✍️ Digital Signature
                  </Form.Label>
                  <div className="d-flex gap-2">
                    <Form.Control
                      as="textarea"
                      rows={2}
                      value={result.signature}
                      readOnly
                      className="font-monospace small"
                    />
                    <Button
                      variant="outline-success"
                      onClick={() => handleCopy(result.signature, 'signature')}
                      style={{ minWidth: '100px' }}
                    >
                      <FaCopy /> {copied.signature ? 'Copied!' : 'Copy'}
                    </Button>
                  </div>
                  <Form.Text className="text-muted">
                    Format: 0xR,0xS (two hex numbers separated by comma)
                  </Form.Text>
                </Form.Group>

                {/* Public Key */}
                <Form.Group className="mb-4">
                  <Form.Label className="fw-bold text-info">
                    🔓 Public Key (Derived from your private key)
                  </Form.Label>
                  <div className="d-flex gap-2">
                    <Form.Control
                      as="textarea"
                      rows={2}
                      value={result.public_key}
                      readOnly
                      className="font-monospace small"
                    />
                    <Button
                      variant="outline-info"
                      onClick={() => handleCopy(result.public_key, 'publicKey')}
                      style={{ minWidth: '100px' }}
                    >
                      <FaCopy /> {copied.publicKey ? 'Copied!' : 'Copy'}
                    </Button>
                  </div>
                  <Form.Text className="text-muted">
                    This public key can be shared and used to verify your signature
                  </Form.Text>
                </Form.Group>

                {/* Next Steps */}
                <Alert variant="info">
                  <h6 className="fw-bold">📝 Next Steps:</h6>
                  <ul className="mb-0">
                    <li>Save the <strong>File Hash</strong> and <strong>Signature</strong></li>
                    <li>If you are a school, you can use these to push diploma to blockchain</li>
                    <li>Anyone can verify this signature using the <a href="/verify">Verify Tool</a></li>
                  </ul>
                </Alert>
              </Card.Body>
            </Card>
          )}

          {/* Information Cards */}
          <div className="row g-3 mt-4">
            <div className="col-md-6">
              <Card className="h-100 border-primary">
                <Card.Body>
                  <h6 className="text-primary fw-bold">🔐 How It Works</h6>
                  <ol className="small text-muted mb-0">
                    <li>Upload your file (PDF, DOCX, etc.)</li>
                    <li>Enter your private key</li>
                    <li>System generates SHA-256 hash of file</li>
                    <li>Sign the hash using ECDSA TNM5224</li>
                    <li>Get signature for verification</li>
                  </ol>
                </Card.Body>
              </Card>
            </div>

            <div className="col-md-6">
              <Card className="h-100 border-warning">
                <Card.Body>
                  <h6 className="text-warning fw-bold">⚠️ Security Notes</h6>
                  <ul className="small text-muted mb-0">
                    <li><strong>Never share</strong> your private key</li>
                    <li>This tool runs <strong>locally</strong> - your key is not stored</li>
                    <li>The signature proves you own the private key</li>
                    <li>Anyone with your public key can verify the signature</li>
                  </ul>
                </Card.Body>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </Container>
  );
};

export default SignFile;
