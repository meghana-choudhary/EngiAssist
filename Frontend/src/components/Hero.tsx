import Chat from "./Chat";
import "../css/hero.css";
import "../css/pdfviewer.css";
// import PdfViewer from "./PdfViewer";
import { useState } from "react";
// import { useNavigate } from 'react-router-dom';

interface Relevant_Files {
  files: { [key: string]: any }[];
  // summary: string;
}

export const Hero = () => {
  // const navigate = useNavigate();
  const [fileList, setFileList] = useState<Relevant_Files>();
  const [filesPresent, setFilePresent] = useState(false);
  // const [fileList, setFileList] = useState<Relevant_Files>();
  // const [showPdf, setShowPdf] = useState(false);
  // const [selectedPdf, setSelectedPdf] = useState<{
  //   a: string;
  //   b: number;
  // } | null>(null);
  // const [filesPresent, setFilePresent] = useState(false);

  // const receiveFiles = (files: { [key: string]: any }[]) => {
  //   console.log(files);
  //   setFilePresent(true);
  //   setFileList({ files: files });
  // };

  const receiveFiles = (files: { [key: string]: any }[]) => {
    console.log(files);
    setFilePresent(true);
    setFileList({ files: files });
  };

  //---------------------For opening pdf in same page and tab-------------------------
  // const returnOptions = (data: Relevant_Files | undefined) => {
  //   if (data) {
  //     return (
  //       <div className="llm-response">
  //         <h3 id="rel-heading">Relevant Documents</h3>
  //         <div className="pdf-section">
  //           {data.files.map((option) => (
  //             <button
  //               className="file-btn"
  //               onClick={() => {
  //                 setShowPdf(true); // Update state
  //                 setSelectedPdf({ a: option.file, b: option.page }); // Store selected PDF data
  //               }}
  //             >
  //               {option.file}_Page {option.page}_Dist:
  //               {option.distance.toFixed(3)}
  //             </button>
  //           ))}

  //           {/* Render PdfViewer outside the event handler */}
  //         </div>
  //         {showPdf && selectedPdf && (
  //           <PdfViewer a={selectedPdf.a} b={selectedPdf.b} />
  //         )}
  //       </div>
  //     );
  //   }
  // };

  //------------For opening pdf in diff page but same tab-------------------

  // const returnOptions = (data: Relevant_Files | undefined) => {
  //   if (data) {
  //     return (
  //       <div className="llm-response">
  //         <h3 id="rel-heading">Relevant Documents</h3>
  //         <div className="pdf-section">
  //           {data.files.map((option, index) => (
  //             <button
  //               key={index}
  //               className="file-btn"
  //               onClick={() => {
  //                 // Instead of setting state, navigate to the PDF viewer page
  //                 navigate(`/pdf/${option.file}/${option.page}`);
  //               }}
  //             >
  //               {option.file}_Page {option.page}_Dist:
  //               {option.distance.toFixed(3)}
  //             </button>
  //           ))}
  //         </div>
  //         {/* Remove the PDF viewer from here */}
  //       </div>
  //     );
  //   }
  // };

  //------------------For opening pdf in diff page and diff tab---------------------------

  const returnOptions = (data: Relevant_Files | undefined) => {
    if (data) {
      return (
        <div className="llm-response">
          <h3 id="rel-heading">Relevant Documents</h3>
          <div className="pdf-section">
            {data.files.map((option, index) => (
              <button
                key={index}
                className="file-btn"
                onClick={() => {
                  // Open the PDF in a new tab
                  window.open(`/pdf/${option.file}/${option.page}`, "_blank");
                }}
              >
                {option.file}_Page {option.page}_Dist:
                {option.distance.toFixed(3)}
              </button>
            ))}
          </div>
        </div>
      );
    }
  };

  return (
    <div className="main">
      <div className="hero">
        <div className="left-panel">
          <div>
            <h1 className="heading">RAG</h1>
          </div>
          <div className="file-list">
            <div id="greet">
              <p>Your personal Document QnA Asistant</p>
            </div>
            <div className="rel-docs">
              {filesPresent && returnOptions(fileList)}
            </div>
            <div></div>
          </div>
        </div>
        <Chat returnOptions={receiveFiles} />
      </div>
    </div>
  );
};
