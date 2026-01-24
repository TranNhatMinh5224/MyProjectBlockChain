import React, { useState } from 'react';
import { Container, Card, Button, Alert, Form, InputGroup } from 'react-bootstrap';
import { FaKey, FaCopy, FaDownload, FaEye, FaEyeSlash } from 'react-icons/fa';
import { cryptoAPI } from '../../services/api';
import { copyToClipboard, downloadText } from '../../utils/helpers';

const CryptoTools = () => {
  const [keypair, setKeypair] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPrivateKey, setShowPrivateKey] = useState(false);
  const [copied, setCopied] = useState({ private: false, public: false });

  const handleGenerateKeypair = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await cryptoAPI.generateKeypair();
      setKeypair(response.data.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate keypair');
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

  const handleDownload = () => {
    const content = `Private Key:\n${keypair.privateKey}\n\nPublic Key:\n${keypair.publicKey}`;
    downloadText(content, 'keypair.txt');
  };

  return (
    <Container className="py-5">
      <h2 className="text-center mb-4 fw-bold">
        <FaKey className="me-2" />
        Cryptography Tools
      </h2>
      <p className="text-center text-muted mb-5">
        Generate keypairs and manage digital signatures using TNM5224 Custom Elliptic Curve
      </p>

      <div className="row justify-content-center">
        <div className="col-lg-8">
          {/* Generate Keypair Card */}
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-primary text-white">
              <h5 className="mb-0">Generate Keypair</h5>
            </Card.Header>
            <Card.Body>
              <p className="text-muted">
                Generate a new keypair using TNM5224 Custom Elliptic Curve (ECDSA)
              </p>
              
              <Button
                variant="primary"
                size="lg"
                onClick={handleGenerateKeypair}
                disabled={loading}
                className="w-100"
              >
                {loading ? 'Generating...' : 'Generate New Keypair'}
              </Button>

              {error && <Alert variant="danger" className="mt-3">{error}</Alert>}

              {keypair && (
                <div className="mt-4">
                  <Alert variant="warning">
                    <strong>⚠️ Important:</strong> Save your private key securely! 
                    You cannot recover it if lost. Never share your private key with anyone.
                  </Alert>

                  {/* Private Key */}
                  <Form.Group className="mb-4">
                    <Form.Label className="fw-bold text-danger">
                      🔒 Private Key (Keep Secret!)
                    </Form.Label>
                    <InputGroup>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        value={keypair.privateKey}
                        readOnly
                        type={showPrivateKey ? 'text' : 'password'}
                        className="font-monospace small"
                      />
                      <Button
                        variant="outline-secondary"
                        onClick={() => setShowPrivateKey(!showPrivateKey)}
                      >
                        {showPrivateKey ? <FaEyeSlash /> : <FaEye />}
                      </Button>
                      <Button
                        variant="outline-primary"
                        onClick={() => handleCopy(keypair.privateKey, 'private')}
                      >
                        <FaCopy /> {copied.private ? 'Copied!' : 'Copy'}
                      </Button>
                    </InputGroup>
                  </Form.Group>

                  {/* Public Key */}
                  <Form.Group className="mb-4">
                    <Form.Label className="fw-bold text-success">
                      🔓 Public Key (Can Share)
                    </Form.Label>
                    <InputGroup>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        value={keypair.publicKey}
                        readOnly
                        className="font-monospace small"
                      />
                      <Button
                        variant="outline-primary"
                        onClick={() => handleCopy(keypair.publicKey, 'public')}
                      >
                        <FaCopy /> {copied.public ? 'Copied!' : 'Copy'}
                      </Button>
                    </InputGroup>
                  </Form.Group>

                  <Button
                    variant="success"
                    onClick={handleDownload}
                    className="w-100"
                  >
                    <FaDownload className="me-2" />
                    Download Keypair as Text File
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Info Cards */}
          <div className="row g-3">
            <div className="col-md-6">
              <Card className="h-100 border-primary">
                <Card.Body>
                  <h6 className="text-primary fw-bold">What is TNM5224?</h6>
                  <p className="small text-muted mb-0">
                    TNM5224 is a custom elliptic curve designed for this blockchain system, 
                    providing secure digital signatures using ECDSA algorithm.
                  </p>
                </Card.Body>
              </Card>
            </div>
            
            <div className="col-md-6">
              <Card className="h-100 border-danger">
                <Card.Body>
                  <h6 className="text-danger fw-bold">Security Tips</h6>
                  <ul className="small text-muted mb-0 ps-3">
                    <li>Never share your private key</li>
                    <li>Store it in a secure location</li>
                    <li>Use it only for signing</li>
                    <li>Public key is safe to share</li>
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

export default CryptoTools;
