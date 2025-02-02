import { ScrollArea } from "@/components/ui/scroll-area"
import { useLogContext } from "@/context/LogContext"

export function LogTab() {
  const { logs } = useLogContext()

  return (
    <div className="border rounded-lg bg-card">
      <ScrollArea className="h-full min-h-screen">
        <div className="p-4 font-mono text-sm space-y-2">
          {logs.map((log, index) => (
            <div 
              key={index} 
              className={`p-2 rounded ${
                log.type === 'error' ? 'bg-destructive/10 text-destructive' :
                log.type === 'success' ? 'bg-green-100 text-green-800' :
                'bg-muted'
              }`}
            >
              <span className="font-medium">
                [{new Date(log.timestamp).toLocaleTimeString()}]
              </span>{' '}
              {log.message}
            </div>
          ))}
          {logs.length === 0 && (
            <div className="text-center text-muted-foreground py-8">
              No logs to display
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
