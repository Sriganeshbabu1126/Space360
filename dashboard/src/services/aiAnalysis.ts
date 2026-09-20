import axios from 'axios';

const ANTHROPIC_API_KEY = process.env.REACT_APP_ANTHROPIC_API_KEY;

export const analyzeVisualChanges = async (imageUrlA: string, imageUrlB: string): Promise<string> => {
  if (!ANTHROPIC_API_KEY) {
    throw new Error("Anthropic API key is not configured.");
  }

  try {
    // Helper to fetch base64
    const fetchBase64 = async (url: string) => {
      const response = await fetch(url);
      const blob = await response.blob();
      return new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    };

    const b64A = await fetchBase64(imageUrlA);
    const b64B = await fetchBase64(imageUrlB);

    const getBase64Data = (dataUrl: string) => {
      const parts = dataUrl.split(',');
      let mediaType = parts[0].split(';')[0].split(':')[1];
      if (!mediaType.includes('image/')) {
         mediaType = 'image/jpeg';
      }
      return { 
        media_type: mediaType as 'image/jpeg' | 'image/png' | 'image/gif' | 'image/webp', 
        data: parts[1] 
      };
    };

    const imgA = getBase64Data(b64A);
    const imgB = getBase64Data(b64B);

    const response = await axios.post(
      'https://api.anthropic.com/v1/messages',
      {
        model: 'claude-3-5-sonnet-20240620',
        max_tokens: 1024,
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'text',
                text: 'Here is the first image (Before):'
              },
              {
                type: 'image',
                source: {
                  type: 'base64',
                  media_type: imgA.media_type,
                  data: imgA.data,
                }
              },
              {
                type: 'text',
                text: 'Here is the second image (After):'
              },
              {
                type: 'image',
                source: {
                  type: 'base64',
                  media_type: imgB.media_type,
                  data: imgB.data,
                }
              },
              {
                type: 'text',
                text: 'Please analyze these two images and describe the key visual changes between the Before and After states. Be concise and focus on structural or significant differences.'
              }
            ]
          }
        ]
      },
      {
        headers: {
          'x-api-key': ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01',
          'content-type': 'application/json',
          'anthropic-dangerous-direct-browser-access': 'true'
        }
      }
    );

    return response.data.content[0].text;
  } catch (error: any) {
    console.error("Failed to analyze changes via Claude API:", error);
    throw new Error(error.response?.data?.error?.message || "Failed to analyze changes.");
  }
};
