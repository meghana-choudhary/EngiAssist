// PdfViewerPage.tsx
import React from 'react';
import { useParams } from 'react-router-dom';
// import { useParams, Link } from 'react-router-dom';
import PdfViewer from './PdfViewer';
import "../css/pdfviewpage.css";

const PdfViewerPage: React.FC = () => {
  const { filename, page } = useParams<{ filename: string; page: string }>();
  
  return (
    <div className="pdf-page-container">
      <div className="pdf-header">
        {/* <Link to="/" className="back-button">← Back to Search</Link> */}
        <h2>Viewing: {filename} (Page {page})</h2>
      </div>
      
      {filename && page && (
        <PdfViewer a={filename} b={parseInt(page, 10)} />
      )}
    </div>
  );
};

export default PdfViewerPage;