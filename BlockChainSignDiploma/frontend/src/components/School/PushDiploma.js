import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Card, Form, Button, Alert, Tabs, Tab } from 'react-bootstrap';
import { FaUpload } from 'react-icons/fa';
import { useAuth } from '../../contexts/AuthContext';
import { schoolAPI, cryptoAPI } from '../../services/api';
import SuccessModal from '../Common/SuccessModal';

const PushDiploma = () => {
  const { user, isActive } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('manual');

  // ... (rest of the state remains same)
  // Manual input state
  const [manualData, setManualData] = useState({
    file_hash: '',
    signature: '',
    diploma_id: '',
    school_id: user?.schoolId || '',
    student_name: '',
    student_id: '',
    major: '',
    grade: '',
    issue_date: '',
  });

  // Auto sign state
  const [autoData, setAutoData] = useState({
    diploma_file: null,
    private_key: '',
    diploma_id: '',
    student_name: '',
    student_id: '',
    major: '',
    grade: '',
    issue_date: '',
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  if (!isActive()) {
    return (
      <Container className="py-5">
        <Alert variant="warning">
          <h4>Account Not Active</h4>
          <p>Your account must be approved by Ministry before you can push diplomas to blockchain.</p>
          <p>Please submit CSR and wait for approval.</p>
        </Alert>
      </Container>
    );
  }

  const handleManualChange = (e) => {
    setManualData({
      ...manualData,
      [e.target.name]: e.target.value,
    });
  };

  const handleAutoChange = (e) => {
    if (e.target.type === 'file') {
      setAutoData({
        ...autoData,
        diploma_file: e.target.files[0],
      });
    } else {
      setAutoData({
        ...autoData,
        [e.target.name]: e.target.value,
      });
    }
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new FormData();
      Object.keys(manualData).forEach((key) => {
        formData.append(key, manualData[key]);
      });

      await schoolAPI.pushToFabric(formData);
      setSuccess(true);
      // Removed auto reload to show modal
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to push diploma to blockchain');
    } finally {
      setLoading(false);
    }
  };

  const handleAutoSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Step 1: Sign the file
      const signFormData = new FormData();
      signFormData.append('file', autoData.diploma_file);
      signFormData.append('private_key', autoData.private_key);

      const signResponse = await cryptoAPI.signFile(signFormData);
      const { file_hash, signature } = signResponse.data.data;

      // Step 2: Push to blockchain
      const pushFormData = new FormData();
      pushFormData.append('file_hash', file_hash);
      pushFormData.append('signature', signature);
      pushFormData.append('diploma_id', autoData.diploma_id);
      pushFormData.append('school_id', user.schoolId);
      pushFormData.append('student_name', autoData.student_name);
      pushFormData.append('student_id', autoData.student_id);
      pushFormData.append('major', autoData.major);
      pushFormData.append('grade', autoData.grade);
      pushFormData.append('issue_date', autoData.issue_date);

      await schoolAPI.pushToFabric(pushFormData);
      setSuccess(true);
      // Removed auto reload to show modal
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to push diploma to blockchain');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="py-5">
      <h2 className="mb-4 fw-bold">
        <FaUpload className="me-2" />
        Push Diploma to Blockchain
      </h2>

      <Card className="shadow-sm">
        <Card.Body className="p-4">
          {error && <Alert variant="danger">{error}</Alert>}
          {/* Success Alert is removed as we use Modal now */}

          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k)}
            className="mb-4"
          >
            {/* Tab 1: Manual Input */}
            <Tab eventKey="manual" title="Manual Input (Pre-signed)">
              <Alert variant="info" className="mt-3">
                Use this if you've already signed your diploma file using Crypto Tools
              </Alert>

              <Form onSubmit={handleManualSubmit}>
                <h5 className="mb-3">Signature Information</h5>

                <Form.Group className="mb-3">
                  <Form.Label>File Hash *</Form.Label>
                  <Form.Control
                    type="text"
                    name="file_hash"
                    value={manualData.file_hash}
                    onChange={handleManualChange}
                    placeholder="SHA-256 hash from signing"
                    required
                    className="font-monospace small"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Signature * (Format: 0xR,0xS)</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={2}
                    name="signature"
                    value={manualData.signature}
                    onChange={handleManualChange}
                    placeholder="0xabcd...,0xef01..."
                    required
                    className="font-monospace small"
                  />
                </Form.Group>

                <hr className="my-4" />

                <h5 className="mb-3">Diploma Information</h5>

                <Form.Group className="mb-3">
                  <Form.Label>Diploma ID *</Form.Label>
                  <Form.Control
                    type="text"
                    name="diploma_id"
                    value={manualData.diploma_id}
                    onChange={handleManualChange}
                    placeholder="e.g., HUST-2025-001234"
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Student Name *</Form.Label>
                  <Form.Control
                    type="text"
                    name="student_name"
                    value={manualData.student_name}
                    onChange={handleManualChange}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Student ID *</Form.Label>
                  <Form.Control
                    type="text"
                    name="student_id"
                    value={manualData.student_id}
                    onChange={handleManualChange}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Major *</Form.Label>
                  <Form.Control
                    type="text"
                    name="major"
                    value={manualData.major}
                    onChange={handleManualChange}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Grade *</Form.Label>
                  <Form.Select
                    name="grade"
                    value={manualData.grade}
                    onChange={handleManualChange}
                    required
                  >
                    <option value="">Select grade...</option>
                    <option value="Xuất sắc">Xuất sắc</option>
                    <option value="Giỏi">Giỏi</option>
                    <option value="Khá">Khá</option>
                    <option value="Trung bình">Trung bình</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>Issue Date *</Form.Label>
                  <Form.Control
                    type="date"
                    name="issue_date"
                    value={manualData.issue_date}
                    onChange={handleManualChange}
                    required
                  />
                </Form.Group>

                <Button
                  variant="primary"
                  type="submit"
                  size="lg"
                  className="w-100"
                  disabled={loading || success}
                >
                  {loading ? 'Pushing to Blockchain...' : 'Push to Blockchain'}
                </Button>
              </Form>
            </Tab>

            {/* Tab 2: Auto Sign & Push */}
            <Tab eventKey="auto" title="Auto Sign & Push">
              <Alert variant="info" className="mt-3">
                Upload your diploma file and private key - we'll sign it and push to blockchain automatically
              </Alert>

              <Form onSubmit={handleAutoSubmit}>
                <h5 className="mb-3">Upload & Sign</h5>

                <Form.Group className="mb-3">
                  <Form.Label>Diploma File (PDF) *</Form.Label>
                  <Form.Control
                    type="file"
                    accept=".pdf"
                    onChange={handleAutoChange}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Private Key *</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={2}
                    name="private_key"
                    value={autoData.private_key}
                    onChange={handleAutoChange}
                    placeholder="0x..."
                    required
                    className="font-monospace small"
                  />
                  <Form.Text className="text-danger">
                    ⚠️ Your private key is used locally for signing and is NOT sent to the server
                  </Form.Text>
                </Form.Group>

                <hr className="my-4" />

                <h5 className="mb-3">Diploma Information</h5>

                <Form.Group className="mb-3">
                  <Form.Label>Diploma ID *</Form.Label>
                  <Form.Control
                    type="text"
                    name="diploma_id"
                    value={autoData.diploma_id}
                    onChange={handleAutoChange}
                    placeholder="e.g., HUST-2025-001234"
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Student Name *</Form.Label>
                  <Form.Control
                    type="text"
                    name="student_name"
                    value={autoData.student_name}
                    onChange={handleAutoChange}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Student ID *</Form.Label>
                  <Form.Control
                    type="text"
                    name="student_id"
                    value={autoData.student_id}
                    onChange={handleAutoChange}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Major *</Form.Label>
                  <Form.Control
                    type="text"
                    name="major"
                    value={autoData.major}
                    onChange={handleAutoChange}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Grade *</Form.Label>
                  <Form.Select
                    name="grade"
                    value={autoData.grade}
                    onChange={handleAutoChange}
                    required
                  >
                    <option value="">Select grade...</option>
                    <option value="Xuất sắc">Xuất sắc</option>
                    <option value="Giỏi">Giỏi</option>
                    <option value="Khá">Khá</option>
                    <option value="Trung bình">Trung bình</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>Issue Date *</Form.Label>
                  <Form.Control
                    type="date"
                    name="issue_date"
                    value={autoData.issue_date}
                    onChange={handleAutoChange}
                    required
                  />
                </Form.Group>

                <Button
                  variant="success"
                  type="submit"
                  size="lg"
                  className="w-100"
                  disabled={loading || success}
                >
                  {loading ? 'Signing & Pushing...' : 'Sign & Push to Blockchain'}
                </Button>
              </Form>
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>

      <SuccessModal
        show={success}
        onHide={() => setSuccess(false)}
        message={
          <>
            Dữ liệu đã được mã hóa, ký số và ghi nhận vĩnh viễn trên hệ thống Hyperledger Fabric.
            <br />
            Bạn đã góp phần nâng cao tính minh bạch cho nền giáo dục! 🚀
          </>
        }
        primaryBtnText="Quản lý danh sách bằng"
        secondaryBtnText="Đóng & Nhập tiếp"
        onPrimaryAction={() => navigate('/school/diplomas')}
        onSecondaryAction={() => setSuccess(false)}
      />
    </Container>
  );
};

export default PushDiploma;
