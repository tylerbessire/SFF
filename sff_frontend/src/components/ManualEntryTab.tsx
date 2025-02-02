import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useForm } from "@/hooks/useForm"
import { useLogContext } from "@/context/LogContext"
import { submitManualEntry, scrapeBusiness } from "@/lib/api/client"
import type { FormState } from "@/lib/api/types"
import { useState } from "react"

export function ManualEntryTab() {
  const [accounts, setAccounts] = useState<FormState[]>([])
  const [selectedAccount, setSelectedAccount] = useState<number | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isScraping, setIsScraping] = useState(false)
  const { addLog } = useLogContext()
  const { formData, handleChange, resetForm } = useForm<FormState>()

  const handleAddAccount = async () => {
    if (!formData.accountNumber && !formData.client && !formData.city) {
      addLog('Please fill in at least one field', 'error')
      return
    }

    setIsSubmitting(true)
    try {
      const validFormData: FormState = {
        accountNumber: formData.accountNumber || undefined,
        client: formData.client || undefined,
        city: formData.city || undefined,
        additionalInfo: formData.additionalInfo
      }
      const response = await submitManualEntry(validFormData)
      if (response.success) {
        setAccounts(prev => [...prev, validFormData])
        addLog(`Added account: ${validFormData.accountNumber || 'Unknown'}`, 'success')
        resetForm()
      } else {
        throw new Error('Failed to add account')
      }
    } catch (error) {
      addLog(`Failed to add account: ${error instanceof Error ? error.message : String(error)}`, 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRemoveAccount = () => {
    if (selectedAccount !== null) {
      const removedAccount = accounts[selectedAccount]
      setAccounts(prev => prev.filter((_, index) => index !== selectedAccount))
      addLog(`Removed account: ${removedAccount.accountNumber || 'Unknown'}`, 'info')
      setSelectedAccount(null)
    }
  }

  const handleScrape = async () => {
    if (!formData.client || !formData.city) {
      addLog('Please provide business name and city for scraping', 'error')
      return
    }

    setIsScraping(true)
    try {
      const result = await scrapeBusiness(formData.client, formData.city)
      if (result.results && result.results.length > 0) {
        const businessInfo = result.results[0]
        handleChange('accountNumber')({ target: { value: businessInfo.license_number } } as React.ChangeEvent<HTMLInputElement>)
        addLog(`Found business license: ${businessInfo.license_number}`, 'success')
      } else {
        addLog('No business license found', 'info')
      }
    } catch (error) {
      addLog(`Scraping failed: ${error instanceof Error ? error.message : String(error)}`, 'error')
    } finally {
      setIsScraping(false)
    }
  }

  return (
    <div className="space-y-6 p-6 border rounded-lg bg-card">
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
          <label className="w-full sm:w-32 font-medium">Account Number:</label>
          <Input 
            type="text" 
            value={formData.accountNumber || ''} 
            onChange={handleChange('accountNumber')} 
            className="flex-1"
            disabled={isSubmitting || isScraping}
          />
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
          <label className="w-full sm:w-32 font-medium">Business Name:</label>
          <Input 
            type="text" 
            value={formData.client || ''} 
            onChange={handleChange('client')} 
            className="flex-1"
            disabled={isSubmitting || isScraping}
          />
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
          <label className="w-full sm:w-32 font-medium">City:</label>
          <Input 
            type="text" 
            value={formData.city || ''} 
            onChange={handleChange('city')} 
            className="flex-1"
            disabled={isSubmitting || isScraping}
          />
        </div>
      </div>

      <div className="flex flex-col sm:flex-row justify-center gap-4">
        <Button 
          variant="default" 
          onClick={handleAddAccount}
          disabled={isSubmitting || isScraping}
          className="w-full sm:w-auto"
        >
          {isSubmitting ? 'Adding...' : 'Add Account'}
        </Button>
        <Button 
          variant="secondary"
          onClick={handleScrape}
          disabled={isSubmitting || isScraping || !formData.client || !formData.city}
          className="w-full sm:w-auto"
        >
          {isScraping ? 'Scraping...' : 'Scrape Business'}
        </Button>
        <Button 
          variant="destructive" 
          onClick={handleRemoveAccount}
          disabled={selectedAccount === null || isSubmitting || isScraping}
          className="w-full sm:w-auto"
        >
          Remove Selected
        </Button>
      </div>

      <ScrollArea className="h-64 border rounded-md">
        <div className="p-4 space-y-2">
          {accounts.map((account, index) => (
            <div 
              key={index}
              className={`p-4 rounded cursor-pointer transition-colors ${
                selectedAccount === index ? 'bg-accent' : 'hover:bg-accent/50'
              }`}
              onClick={() => setSelectedAccount(index)}
            >
              <p className="font-medium">Account: {account.accountNumber || 'N/A'}</p>
              <p>Business: {account.client || 'N/A'}</p>
              <p>City: {account.city || 'N/A'}</p>
            </div>
          ))}
          {accounts.length === 0 && (
            <div className="text-center text-muted-foreground py-8">
              No accounts added yet
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
