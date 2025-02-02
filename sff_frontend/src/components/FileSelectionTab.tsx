import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import { useLogContext } from "@/context/LogContext"
import { Upload, FolderOpen } from "lucide-react"
import { useRef, useState } from "react"
import { uploadFiles, generatePDF } from "@/lib/api/client"

export function FileSelectionTab() {
  const [inputFile, setInputFile] = useState<File | null>(null)
  const [templateFile, setTemplateFile] = useState<File | null>(null)
  const [outputPath, setOutputPath] = useState<string>("")
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const inputFileRef = useRef<HTMLInputElement>(null)
  const templateFileRef = useRef<HTMLInputElement>(null)
  const { addLog } = useLogContext()

  const handleInputFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const validTypes = ['.csv', '.xlsx', '.xls', '.docx', '.txt']
      const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
      
      if (!validTypes.includes(fileExt)) {
        addLog(`Invalid file type. Please select: ${validTypes.join(', ')}`, 'error')
        return
      }
      
      setInputFile(file)
      addLog(`Selected input file: ${file.name}`, 'info')
    }
  }

  const handleTemplateFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        addLog('Template must be a PDF file', 'error')
        return
      }
      
      setTemplateFile(file)
      addLog(`Selected template file: ${file.name}`, 'info')
    }
  }

  const handleSubmit = async () => {
    if (!inputFile || !templateFile || !outputPath) {
      addLog('Please select all required files and specify output path', 'error')
      return
    }

    setIsProcessing(true)
    try {
      // Upload files and get processed data
      setUploadProgress(10)
      const uploadResult = await uploadFiles(inputFile, templateFile, outputPath)
      setUploadProgress(50)
      addLog('Files uploaded successfully', 'success')

      // Generate PDFs for each record
      const totalRecords = uploadResult.data.length;
      for (let i = 0; i < totalRecords; i++) {
        const record = uploadResult.data[i];
        try {
          const pdfBlob = await generatePDF(templateFile.name, record);
          const url = window.URL.createObjectURL(pdfBlob);
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `${record.BUSINESS_NAME || `record_${i + 1}`}.pdf`);
          document.body.appendChild(link);
          link.click();
          link.remove();
          window.URL.revokeObjectURL(url);
          
          setUploadProgress(50 + Math.floor((i + 1) / totalRecords * 40));
          addLog(`Generated PDF for ${record.BUSINESS_NAME || `record ${i + 1}`}`, 'success');
        } catch (error) {
          addLog(`Failed to generate PDF for ${record.BUSINESS_NAME || `record ${i + 1}`}: ${error instanceof Error ? error.message : String(error)}`, 'error');
        }
      }

      setUploadProgress(100)
      addLog('PDF generated and downloaded successfully', 'success')
    } catch (error) {
      addLog(`Error processing files: ${error instanceof Error ? error.message : String(error)}`, 'error')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="space-y-6 p-6 border rounded-lg bg-card">
      <div className="space-y-4">
        <div className="space-y-2">
          <label className="font-medium">Input File:</label>
          <div className="flex gap-4">
            <Input
              type="text"
              value={inputFile?.name || ''}
              placeholder="Select input file (CSV, XLSX, DOCX, TXT)"
              readOnly
              className="flex-1"
            />
            <Button
              variant="secondary"
              onClick={() => inputFileRef.current?.click()}
              disabled={isProcessing}
            >
              <Upload className="mr-2 size-4" />
              Browse
            </Button>
            <input
              ref={inputFileRef}
              type="file"
              accept=".csv,.xlsx,.xls,.docx,.txt"
              className="hidden"
              onChange={handleInputFileChange}
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="font-medium">PDF Template:</label>
          <div className="flex gap-4">
            <Input
              type="text"
              value={templateFile?.name || ''}
              placeholder="Select PDF template"
              readOnly
              className="flex-1"
            />
            <Button
              variant="secondary"
              onClick={() => templateFileRef.current?.click()}
              disabled={isProcessing}
            >
              <Upload className="mr-2 size-4" />
              Browse
            </Button>
            <input
              ref={templateFileRef}
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleTemplateFileChange}
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="font-medium">Output Path:</label>
          <div className="flex gap-4">
            <Input
              type="text"
              value={outputPath}
              onChange={(e) => setOutputPath(e.target.value)}
              placeholder="Specify output folder path"
              className="flex-1"
              disabled={isProcessing}
            />
            <Button variant="secondary" disabled={isProcessing}>
              <FolderOpen className="mr-2 size-4" />
              Browse
            </Button>
          </div>
        </div>
      </div>

      {uploadProgress > 0 && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Upload Progress</span>
            <span>{uploadProgress}%</span>
          </div>
          <Progress value={uploadProgress} />
        </div>
      )}

      <div className="flex justify-center">
        <Button 
          onClick={handleSubmit} 
          className="w-full sm:w-auto"
          disabled={isProcessing || !inputFile || !templateFile || !outputPath}
        >
          {isProcessing ? 'Processing...' : 'Process Files'}
        </Button>
      </div>
    </div>
  )
}
