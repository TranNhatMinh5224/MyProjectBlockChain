import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

// Layout Components
import NavigationBar from './components/Layout/Navbar';
import Footer from './components/Layout/Footer';
import PrivateRoute from './components/Layout/PrivateRoute';

// Auth Components
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';

// Public Components
import Home from './components/Home';
import CryptoTools from './components/Crypto/CryptoTools';
import SignFile from './components/Crypto/SignFile';
import VerifyDiploma from './components/Verify/VerifyDiploma';

// School Components
import SchoolDashboard from './components/School/SchoolDashboard';
import SubmitCSR from './components/School/SubmitCSR';
import PushDiploma from './components/School/PushDiploma';
import SchoolDiplomas from './components/School/SchoolDiplomas';

// Ministry Components
import MinistryDashboard from './components/Ministry/MinistryDashboard';
import MinistryCSRManagement from './components/Ministry/MinistryCSRManagement';
import MinistrySchools from './components/Ministry/MinistrySchools';

// Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="d-flex flex-column min-vh-100">
          <NavigationBar />
          <main className="flex-grow-1">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/crypto-tools" element={<CryptoTools />} />
              <Route path="/sign-file" element={<SignFile />} />
              <Route path="/verify" element={<VerifyDiploma />} />

              {/* School Routes */}
              <Route
                path="/school/dashboard"
                element={
                  <PrivateRoute requireSchool>
                    <SchoolDashboard />
                  </PrivateRoute>
                }
              />
              <Route
                path="/school/csr"
                element={
                  <PrivateRoute requireSchool>
                    <SubmitCSR />
                  </PrivateRoute>
                }
              />
              <Route
                path="/school/push-diploma"
                element={
                  <PrivateRoute requireSchool requireActive>
                    <PushDiploma />
                  </PrivateRoute>
                }
              />
              <Route
                path="/school/diplomas"
                element={
                  <PrivateRoute requireSchool>
                    <SchoolDiplomas />
                  </PrivateRoute>
                }
              />

              {/* Ministry Routes */}
              <Route
                path="/ministry/dashboard"
                element={
                  <PrivateRoute requireMinistry>
                    <MinistryDashboard />
                  </PrivateRoute>
                }
              />
              <Route
                path="/ministry/csr"
                element={
                  <PrivateRoute requireMinistry>
                    <MinistryCSRManagement />
                  </PrivateRoute>
                }
              />
              <Route
                path="/ministry/schools"
                element={
                  <PrivateRoute requireMinistry>
                    <MinistrySchools />
                  </PrivateRoute>
                }
              />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
