import Chat from "./Chat";
import "../css/hero.css";
import "../css/pdfviewer.css";
import { useState } from "react";
import logo from "../assets/engi.jpg";

interface Relevant_Files {
  files: { [key: string]: any }[];
}

export const Hero = () => {
  const [fileList, setFileList] = useState<Relevant_Files>();
  const [filesPresent, setFilePresent] = useState(false);

  const receiveFiles = (files: { [key: string]: any }[]) => {
    console.log(files);
    setFilePresent(true);
    setFileList({ files: files });
  };

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
            <img src={logo} alt="logo" className="logo" />
          </div>
          <div className="file-list">
            <div id="greet">
              <p>Feeling stuck on your assignments? Let us help!</p>
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
