import "../css/pdfviewer.css"

interface PdfViewerProps {
  a: string;
  b: number;
}

const PdfViewer: React.FC<PdfViewerProps> = ({ a, b }) => {
  
  return (
    <div className="App">
      <div id="my-pdf">
        <iframe
          src={`/${a}.pdf?page=${b}#page=${b}`}
          title="Hello"
        ></iframe>
      </div>
    </div>
  );
};

export default PdfViewer;
