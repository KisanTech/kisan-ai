interface AgentMessage {
  role: 'user' | 'assistant';
  parts: Array<{
    text: string;
  }>;
}

interface AgentPayload {
  appName: string;
  userId: string;
  sessionId: string;
  newMessage: AgentMessage;
}

interface AgentResponse {
  response?: {
    candidates?: Array<{
      content?: {
        parts?: Array<{
          text?: string;
        }>;
      };
    }>;
  };
  [key: string]: any;
}

class AIService {
  private readonly baseUrl = 'http://localhost:8000';
  private readonly userId = 'u_123';
  private readonly sessionId = 's_123';
  private readonly appName = 'crop_diagnosis_agent';

  /**
   * Create or ensure session exists
   */
  private async createSession(): Promise<void> {
    try {
      const sessionUrl = `${this.baseUrl}/apps/${this.appName}/users/${this.userId}/sessions/${this.sessionId}`;

      const response = await fetch(sessionUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}), // Empty body for session creation
      });

      if (!response.ok) {
        // Session might already exist, which is fine
        console.log('Session creation response:', response.status);
      }
    } catch (error) {
      console.error('Error creating session:', error);
      // Don't throw here as session might already exist
    }
  }

  /**
   * Call the agent with a message
   */
  private async callAgentEndpoint(payload: AgentPayload): Promise<AgentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Agent call failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error calling agent:', error);
      throw new Error('Failed to get response from AI agent');
    }
  }

  /**
   * Generic method to call the crop diagnosis agent with base64 image data
   */
  async callAgent(base64Image: string, description?: string): Promise<any> {
    try {
      console.log('Starting agent call with base64 image, length:', base64Image.length);

      // Step 1: Create session
      await this.createSession();
      console.log('Session created/verified');

      // Step 2: Prepare message text with image and description
      let messageText = `Analyze this crop image for disease diagnosis.

Image Data: data:image/jpeg;base64,${base64Image}`;

      if (description) {
        messageText += `\n\nContext: ${description}`;
      }

      // Step 3: Prepare payload
      const payload: AgentPayload = {
        appName: this.appName,
        userId: this.userId,
        sessionId: this.sessionId,
        newMessage: {
          role: 'user',
          parts: [
            {
              text: messageText,
            },
          ],
        },
      };

      console.log('Calling agent with payload...');

      // Step 4: Call agent
      const response = await this.callAgentEndpoint(payload);
      console.log('Agent response received:', response);

      // Step 5: Extract and parse response - Updated for actual Agent API structure
      // The response is an array with the agent response as the first element
      const agentResponse = response[0];
      const agentResponseText = agentResponse?.content?.parts?.[0]?.text;

      if (!agentResponseText) {
        throw new Error('No response received from agent');
      }

      console.log('Raw agent response:', agentResponseText.substring(0, 200) + '...');

      // Try to parse JSON response from agent - Handle markdown code blocks
      try {
        // Remove markdown code blocks if present (```json ... ```)
        let cleanJsonText = agentResponseText;

        // Check if response is wrapped in markdown code blocks
        if (agentResponseText.includes('```json')) {
          const jsonMatch = agentResponseText.match(/```json\s*([\s\S]*?)\s*```/);
          if (jsonMatch && jsonMatch[1]) {
            cleanJsonText = jsonMatch[1].trim();
          }
        }

        const parsedResponse = JSON.parse(cleanJsonText);
        console.log('Successfully parsed JSON response');
        return parsedResponse;
      } catch (parseError) {
        console.warn('Response was not valid JSON, returning raw text');
        // If not JSON, return the raw text in a structured format
        return {
          success: false,
          rawResponse: agentResponseText,
          error: 'Response was not in JSON format',
          message: 'The AI agent provided a response but it was not in the expected format.',
        };
      }
    } catch (error) {
      console.error('Agent call failed:', error);

      // Return a structured error response
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        message: 'Failed to get diagnosis from AI agent. Please try again.',
      };
    }
  }

  /**
   * Specific method for crop diagnosis (for backward compatibility)
   */
  async diagnoseCrop(base64Image: string, description?: string): Promise<any> {
    return this.callAgent(base64Image, description);
  }
}

// Export singleton instance
export const aiService = new AIService();
export default aiService;
