import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useForm } from "@/hooks/useForm"
import { useLogContext } from "@/context/LogContext"

const textFields = [
  "Old Account #", "Old DBA Name", "Account Number for Changes only",
  "Buyer", "Receiving Times", "Special Instructions", "Phone Number",
  "Route #", "Salesperson", "Account Number"
] as const;

const checkboxGroups = {
  "Account Type": ["New Account", "Close Account", "Change or Add Info"],
  "Delivery Location": ["Front", "Back", "Side"],
  "Delivery Days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
  "Credit Application": ["Yes", "No"],
  "Sale Status": ["On Sale", "Off-Sale"],
  "Draft Status": ["Ours", "Theirs", "Ours & Theirs", "Other"],
  "Market Type": ["Bar", "Restaurant", "Grocery", "Deli", "Convenience", "Other"],
  "Buying Status": ["Yes", "No"]
} as const;

export function AdditionalInfoTab() {
  const { formData, handleAdditionalInfoChange, handleCheckboxChange } = useForm()
  const { addLog } = useLogContext()

  const handleSave = () => {
    addLog('Additional information saved', 'success')
  }

  return (
    <div className="min-h-screen">
      <ScrollArea className="h-full">
        <div className="space-y-6 p-6 border rounded-lg bg-card">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {textFields.map((field) => (
              <div key={field} className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                <label className="w-full sm:w-32 font-medium">{field}:</label>
                <Input 
                  type="text" 
                  name={field}
                  value={(formData.additionalInfo?.[field] as string) || ''} 
                  onChange={(e) => handleAdditionalInfoChange(field)(e)}
                  className="flex-1"
                />
              </div>
            ))}
          </div>

          <div className="space-y-6">
            {Object.entries(checkboxGroups).map(([group, options]) => (
              <div key={group} className="space-y-2">
                <h3 className="font-medium text-lg">{group}</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {options.map((option) => {
                    const fieldId = `${group}-${option}`;
                    return (
                      <div key={fieldId} className="flex items-center gap-2">
                        <Checkbox 
                          id={fieldId}
                          checked={!!formData.additionalInfo?.[fieldId]}
                          onCheckedChange={(checked) => {
                            const event = {
                              target: {
                                checked: checked === true
                              }
                            } as React.ChangeEvent<HTMLInputElement>;
                            handleCheckboxChange(fieldId)(event);
                          }}
                        />
                        <label 
                          htmlFor={fieldId}
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          {option}
                        </label>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-center pt-4">
            <Button onClick={handleSave} className="w-full sm:w-auto">
              Save Information
            </Button>
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}
