import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { FileSelectionTab } from "./components/FileSelectionTab"
import { ManualEntryTab } from "./components/ManualEntryTab"
import { AdditionalInfoTab } from "./components/AdditionalInfoTab"
import { LogTab } from "./components/LogTab"
import { LogProvider } from "./context/LogContext"

function App() {
  return (
    <LogProvider>
      <div className="container mx-auto py-6">
        <h1 className="text-2xl font-bold mb-6">Saccani Form Filler</h1>
        
        <Tabs defaultValue="file-selection" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="file-selection">File Selection</TabsTrigger>
            <TabsTrigger value="manual-entry">Manual Entry</TabsTrigger>
            <TabsTrigger value="additional-info">Additional Info</TabsTrigger>
            <TabsTrigger value="log">Log</TabsTrigger>
          </TabsList>
          
          <TabsContent value="file-selection">
            <FileSelectionTab />
          </TabsContent>
          
          <TabsContent value="manual-entry">
            <ManualEntryTab />
          </TabsContent>
          
          <TabsContent value="additional-info">
            <AdditionalInfoTab />
          </TabsContent>
          
          <TabsContent value="log">
            <LogTab />
          </TabsContent>
        </Tabs>
      </div>
    </LogProvider>
  )
}

export default App
