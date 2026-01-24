import React from 'react';
import { Container } from 'react-bootstrap';
import { FaGithub, FaLinkedin } from 'react-icons/fa';

const Footer = () => {
  return (
    <footer className="bg-dark text-white mt-5 py-4">
      <Container>
        <div className="row">
          <div className="col-md-6">
            <h5>Blockchain Diploma Management System</h5>
            <p className="text-muted">
              Hệ thống quản lý văn bằng dựa trên Hyperledger Fabric Blockchain với chữ ký số Custom Elliptic Curve TNM5224
            </p>
          </div>
          <div className="col-md-3">
            <h6>Features</h6>
            <ul className="list-unstyled">
              <li>🏛️ Ministry Management</li>
              <li>🏫 School Management</li>
              <li>🎓 Diploma Issuance</li>
              <li>✅ Diploma Verification</li>
            </ul>
          </div>
          <div className="col-md-3">
            <h6>Technology</h6>
            <ul className="list-unstyled">
              <li>Hyperledger Fabric</li>
              <li>TNM5224 Curve</li>
              <li>ECDSA Algorithm</li>
              <li>React.js + Bootstrap</li>
            </ul>
          </div>
        </div>
        <hr className="bg-white" />
        <div className="text-center">
          <p className="mb-0">
            &copy; 2026 Blockchain Diploma System. All rights reserved.
          </p>
        </div>
      </Container>
    </footer>
  );
};

export default Footer;
