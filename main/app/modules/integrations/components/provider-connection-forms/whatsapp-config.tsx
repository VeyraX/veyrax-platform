import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { RefreshCw, Smartphone, Check, LogOut } from "lucide-react";
import { authenticateWhatsApp, checkWhatsAppStatus, disconnectProvider, enableWhatsapp } from "../../api/api.integrations";

interface WhatsAppConfig {
  phone?: string;
  isLoggedIn: boolean;
}

interface WhatsAppConfigFormProps {
  providerId: string;
  config: WhatsAppConfig;
  onChange: (config: WhatsAppConfig) => void;
  disabled?: boolean;
  onUpdate?: () => void;
  encrypted_api_key?: string;
  code?: string;
}

export function WhatsAppConfigForm({ providerId, config, onChange, disabled = false, onUpdate, encrypted_api_key, code }: WhatsAppConfigFormProps) {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [qrImageData, setQrImageData] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(config.isLoggedIn);
  const [showSuccessAnimation, setShowSuccessAnimation] = useState<boolean>(false);
  const [isDisconnecting, setIsDisconnecting] = useState<boolean>(false);
  const [pollingIntervalId, setPollingIntervalId] = useState<NodeJS.Timeout | null>(null);
  
  // Check connection status on mount
  useEffect(() => {
    if (!disabled && providerId) {
      checkConnectionStatus();
    }
  }, [disabled, providerId]);

  // Clean up interval on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalId) {
        clearInterval(pollingIntervalId);
      }
    };
  }, [pollingIntervalId]);

  const checkConnectionStatus = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await checkWhatsAppStatus(encrypted_api_key, code);
      
      if (result.success) {
        const newConfig = {
          ...config,
          isLoggedIn: result.isLoggedIn || false,
          phone: result.phone
        };
        
        setIsAuthenticated(result.isLoggedIn || false);
        onChange(newConfig);
        
        // If not logged in, automatically start authentication
        if (!result.isLoggedIn) {
          handleAuthenticate();
        }
      } else {
        console.warn("WhatsApp status check returned error:", result.message);
        setError(result.message || "Failed to check WhatsApp status");
      }
    } catch (error) {
      console.error("Error checking WhatsApp status:", error);
      setError(error instanceof Error ? error.message : "Failed to check status");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAuthenticate = async () => {
    setIsLoading(true);
    setError(null);
    setQrImageData(null);
    
    try {
      const result = await authenticateWhatsApp(encrypted_api_key, code);
      
      if (!result.success) {
        setError(result.message || "Failed to start WhatsApp authentication");
        return;
      }
      
      if (result.isLoggedIn) {
        // Already logged in
        handleAuthenticationSuccess();
      } else if (result.qrImageBase64) {
        // Use image base64 for QR code
        setQrImageData(result.qrImageBase64);
        startStatusPolling();
      } else {
        setError("No QR code data received from server");
      }
    } catch (error) {
      console.error("Error during WhatsApp authentication:", error);
      setError(error instanceof Error ? error.message : "Authentication failed");
    } finally {
      setIsLoading(false);
    }
  };

  const startStatusPolling = () => {
    // Clear any existing interval
    if (pollingIntervalId) {
      clearInterval(pollingIntervalId);
    }

    const statusInterval = setInterval(async () => {
      try {
        const statusResult = await checkWhatsAppStatus(encrypted_api_key, code);
        
        if (statusResult.success && statusResult.isLoggedIn) {
          // Clear the interval
          clearInterval(statusInterval);
          setPollingIntervalId(null);
          
          // Call enableWhatsapp once when authentication completes
          try {
            const enableResult = await enableWhatsapp(statusResult, encrypted_api_key, code);
          } catch (enableError) {
            console.error("Failed to enable WhatsApp:", enableError);
          }
          
          handleAuthenticationSuccess();
        }
      } catch (error) {
        console.error("Error checking WhatsApp status during polling:", error);
      }
    }, 5000); // Check every 5 seconds
    
    // Store interval ID in state
    setPollingIntervalId(statusInterval);
  };

  const handleAuthenticationSuccess = () => {
    // Update authentication state
    setIsAuthenticated(true);
    
    // Show success animation
    setShowSuccessAnimation(true);
    
    // Update config
    const newConfig = {
      ...config,
      isLoggedIn: true
    };
    onChange(newConfig);
    
    // After 2 seconds, hide animation and call onUpdate
    setTimeout(() => {
      setShowSuccessAnimation(false);
      if (onUpdate) {
        onUpdate();
      }
    }, 2000);
  };


  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      
      {showSuccessAnimation ? (
        <div className="flex flex-col items-center p-6 border rounded bg-green-50 transition-all duration-500">
          <div className="flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-green-100">
            <Check className="h-8 w-8 text-green-500" />
          </div>
          <h3 className="text-xl font-semibold mb-2 text-green-700">Authentication Successful!</h3>
          <p className="text-sm text-green-600">WhatsApp has been successfully connected</p>
        </div>
      ) : isAuthenticated ? (
        <div className="flex flex-col space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Smartphone className="h-5 w-5 text-green-400" aria-hidden="true" />
              </div>
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-medium text-green-800">WhatsApp Connected</h3>
                {config.phone && (
                  <div className="mt-2 text-sm text-green-700">
                    Phone Number: {config.phone}
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex flex-col space-y-4 p-4 border rounded-md">
            <h3 className="text-sm font-medium">WhatsApp Connection Management</h3>
            
            <p className="text-sm text-gray-500">
              Your WhatsApp account is currently connected. You can disconnect it at any time.
              Disconnecting will require you to scan the QR code again to reconnect.
            </p>
        
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center p-4 border rounded">
          <h3 className="text-xl font-semibold mb-2">Login to WhatsApp</h3>
          <p className="text-sm text-gray-500 mb-2 text-center">Scan this QR code to link an existing WhatsApp account with this device.</p>
          <p className="text-sm text-gray-500 mb-2 text-center">If you will receivie an issue «Can't link this device», please try to close window, open and scan the QR code again.</p>
          
          <div className="mb-2">
            <a href="https://faq.whatsapp.com/1317564962315842/?locale=en_US&cms_platform=web" 
               target="_blank" 
               rel="noopener noreferrer"
               className="text-sm text-blue-600 hover:underline">
              Learn more
            </a>
          </div>
          
          <div className="flex flex-col items-center min-w-[256px] min-h-[256px] bg-white p-4 rounded">
            {isLoading ? (
              <div className="w-64 h-64 bg-gray-200 rounded animate-pulse"></div>
            ) : qrImageData ? (
              <img 
                src={qrImageData.startsWith('data:') ? qrImageData : `data:image/png;base64,${qrImageData}`}
                alt="WhatsApp QR Code"
                className="w-64 h-64"
                onError={() => {
                  console.error("QR code image failed to load");
                  setError("Failed to load QR code image. Please try again.");
                }}
              />
            ) : (
              <div className="w-64 h-64 flex items-center justify-center">
                <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            )}
          </div>
          
          <div className="text-sm text-left w-full space-y-2 mt-2">
            <p>1. Open <img src='/provider-logos/whatsapp.png' className="inline-block h-4 w-4 -mr-1 -mt-1" alt="WhatsApp" /> <strong>WhatsApp</strong> on your phone</p>
            <p>2. Tap <strong>Settings</strong> ⚙️ on iPhone, or <strong>Menu</strong> ⋮ on Android</p>
            <p>3. Tap <strong>Linked devices</strong> and then <strong>Link a device</strong></p>
            <p>4. Point your phone at this screen to scan the QR code</p>
            <p>5. Keep both apps open and connected to the internet (Wi-Fi, 4G or faster) while your chats load.</p>
          </div>
        </div>
      )}
    </div>
  );
}