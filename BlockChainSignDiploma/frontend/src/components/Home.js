import React from 'react';
import { Container, Card, Button, Row, Col, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaShieldAlt, FaUniversity, FaCheckCircle, FaKey, FaSchool } from 'react-icons/fa';

const Home = () => {
  return (
    <div>
      {/* Hero Section */}
      <div className="bg-primary text-white py-5">
        <Container>
          <Row className="align-items-center">
            <Col md={6}>
              <h1 className="display-4 fw-bold mb-4">
                Blockchain Diploma Management System
              </h1>
              <p className="lead mb-4">
                Hệ thống quản lý văn bằng an toàn, minh bạch dựa trên Hyperledger Fabric Blockchain với chữ ký số TNM5224
              </p>
              <div className="d-flex gap-3">
                <Button as={Link} to="/verify" variant="light" size="lg">
                  <FaCheckCircle className="me-2" />
                  Verify Diploma
                </Button>
                <Button as={Link} to="/register" variant="outline-light" size="lg">
                  <FaSchool className="me-2" />
                  Register School
                </Button>
              </div>
            </Col>
            <Col md={6} className="text-center">
              <FaShieldAlt size={200} className="text-white opacity-75" />
            </Col>
          </Row>
        </Container>
      </div>

      {/* Features Section */}
      <Container className="py-5">
        <h2 className="text-center mb-5 fw-bold">Key Features</h2>
        <Row className="g-4">
          <Col md={4}>
            <Card className="h-100 shadow-sm border-0">
              <Card.Body className="text-center p-4">
                <FaUniversity size={50} className="text-primary mb-3" />
                <h4>Ministry Management</h4>
                <p className="text-muted">
                  Bộ Giáo Dục quản lý và phê duyệt các trường đại học, cấp certificate cho trường hợp lệ
                </p>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={4}>
            <Card className="h-100 shadow-sm border-0">
              <Card.Body className="text-center p-4">
                <FaSchool size={50} className="text-success mb-3" />
                <h4>School Management</h4>
                <p className="text-muted">
                  Trường đại học cấp bằng cấp với chữ ký số, đưa metadata lên blockchain immutable
                </p>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={4}>
            <Card className="h-100 shadow-sm border-0">
              <Card.Body className="text-center p-4">
                <FaCheckCircle size={50} className="text-info mb-3" />
                <h4>Public Verification</h4>
                <p className="text-muted">
                  Nhà tuyển dụng và công chúng có thể xác minh tính hợp lệ của bằng cấp
                </p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      {/* Technology Section */}
      <div className="bg-light py-5">
        <Container>
          <h2 className="text-center mb-5 fw-bold">Technology Stack</h2>
          <Row className="g-4">
            <Col md={3}>
              <Card className="text-center border-0 bg-transparent">
                <Card.Body>
                  <div className="display-6 mb-3">⛓️</div>
                  <h5>Hyperledger Fabric</h5>
                  <p className="text-muted small">Enterprise Blockchain</p>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={3}>
              <Card className="text-center border-0 bg-transparent">
                <Card.Body>
                  <div className="display-6 mb-3">🔐</div>
                  <h5>TNM5224 Curve</h5>
                  <p className="text-muted small">Custom Elliptic Curve</p>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={3}>
              <Card className="text-center border-0 bg-transparent">
                <Card.Body>
                  <div className="display-6 mb-3">🔏</div>
                  <h5>ECDSA</h5>
                  <p className="text-muted small">Digital Signature Algorithm</p>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={3}>
              <Card className="text-center border-0 bg-transparent">
                <Card.Body>
                  <div className="display-6 mb-3">⚛️</div>
                  <h5>React.js</h5>
                  <p className="text-muted small">Modern Frontend</p>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </div>

      {/* How It Works */}
      <Container className="py-5">
        <h2 className="text-center mb-5 fw-bold">How It Works</h2>
        <Row className="g-4">
          <Col md={3}>
            <Card className="h-100 text-center shadow-sm">
              <Card.Body>
                <div className="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '60px', height: '60px'}}>
                  <h3 className="mb-0">1</h3>
                </div>
                <h5>School Registration</h5>
                <p className="text-muted small">
                  Trường đăng ký tài khoản và nộp CSR cho Bộ GD
                </p>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={3}>
            <Card className="h-100 text-center shadow-sm">
              <Card.Body>
                <div className="bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '60px', height: '60px'}}>
                  <h3 className="mb-0">2</h3>
                </div>
                <h5>Ministry Approval</h5>
                <p className="text-muted small">
                  Bộ GD xem xét và phê duyệt, cấp certificate
                </p>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={3}>
            <Card className="h-100 text-center shadow-sm">
              <Card.Body>
                <div className="bg-info text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '60px', height: '60px'}}>
                  <h3 className="mb-0">3</h3>
                </div>
                <h5>Issue Diploma</h5>
                <p className="text-muted small">
                  Trường ký và đưa bằng cấp lên blockchain
                </p>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={3}>
            <Card className="h-100 text-center shadow-sm">
              <Card.Body>
                <div className="bg-warning text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '60px', height: '60px'}}>
                  <h3 className="mb-0">4</h3>
                </div>
                <h5>Verify Anytime</h5>
                <p className="text-muted small">
                  Công chúng verify bằng cấp mọi lúc mọi nơi
                </p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      {/* CTA Section */}
      <div className="bg-primary text-white py-5">
        <Container className="text-center">
          <h2 className="mb-4">Ready to Get Started?</h2>
          <p className="lead mb-4">
            <Badge bg="light" text="dark" className="me-2">Public Access</Badge>
            Try our crypto tools without logging in, or register as a school
          </p>
          <div className="d-flex gap-3 justify-content-center flex-wrap">
            <Button as={Link} to="/crypto-tools" variant="light" size="lg">
              <FaKey className="me-2" />
              Generate Keypair
            </Button>
            <Button as={Link} to="/sign-file" variant="light" size="lg">
              Sign a File
            </Button>
            <Button as={Link} to="/verify" variant="outline-light" size="lg">
              Verify Diploma
            </Button>
            <Button as={Link} to="/register" variant="outline-light" size="lg">
              <FaSchool className="me-2" />
              Register as School
            </Button>
          </div>
        </Container>
      </div>
    </div>
  );
};

export default Home;
