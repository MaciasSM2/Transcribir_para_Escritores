import { apiRequest } from '@/lib/api';

interface IDocumentApi {
  saveDocument(text: string, toneName: string): Promise<boolean>;
}

class DocumentApiService implements IDocumentApi {
  public async saveDocument(text: string, toneName: string): Promise<boolean> {
    if (!text) return false;
    
    try {
      const title = `Documento_${new Date().toLocaleDateString('es-MX').replace(/\//g, '-')}`;
      
      const response = await apiRequest('/docs/save', {
        method: 'POST',
        body: JSON.stringify({ text, tone_name: toneName, title }),
      });
      
      if (response.ok) {
        return true;
      }
      
      const errorData = await response.json().catch(() => null);
      console.error('[DocumentApiService] Backend error:', errorData);
      
    } catch (e) {
      console.error('[DocumentApiService] Network error:', e);
    }
    
    return false;
  }
}

export const documentApiService = new DocumentApiService();
